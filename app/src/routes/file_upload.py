from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
from datetime import datetime

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt"}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/ingest")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload PDF and TXT files.
    Accepts multiple files in a single request.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    saved_files = []
    
    for file in files:
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed: {file.filename}. Only .pdf and .txt files are allowed."
            )
        
        # Create a unique filename to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            saved_files.append({
                "filename": file.filename,
                "saved_as": filename,
                "content_type": file.content_type,
                "size": len(content)
            })
            
        except Exception as e:
            # If there's an error, clean up any files that were saved
            for saved_file in saved_files:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, saved_file["saved_as"]))
                except:
                    pass
            
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while processing {file.filename}: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(saved_files)} file(s)",
        "files": saved_files
    }
