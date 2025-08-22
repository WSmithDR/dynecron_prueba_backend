import os
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status

from .extract_text import extract_text_from_pdf
from .save_document import save_document

# Configuration
ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

def is_extension_allowed(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def process_uploaded_file(upload_folder: str, file: UploadFile) -> Dict[str, Any]:
    try:
        # Validate file
        if not file.filename or not is_extension_allowed(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
            
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
            )
        
        # Process based on file type
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            text = extract_text_from_pdf(content)
        elif file_extension == 'txt':
            text = content.decode('utf-8')
        else:
            text = ""
        
        # Prepare metadata
        metadata = {
            'original_filename': file.filename,
            'content_type': file.content_type,
            'file_size': len(content),
            'file_extension': file_extension
        }
        
        # Save the processed document
        file_path = save_document(upload_folder, metadata, text)
        
        return {
            'success': True,
            'message': 'File processed successfully',
            'filename': file.filename,
            'file_path': file_path,
            'content_length': len(text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing file {file.filename}: {str(e)}"
        print(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
