import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

def save_document(upload_folder: str, metadata: Dict[str, Any], content: str) -> str:
    try:
        # Ensure the upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Get original filename and clean it
        original_filename = metadata.get('original_filename', 'document')
        
        # Remove extension and clean the base name
        base_name, ext = os.path.splitext(original_filename)
        safe_base = "".join(c if c.isalnum() or c in ' _-.' else '_' for c in base_name)
        safe_ext = "".join(c.lower() for c in ext if c.isalnum() or c in '_.')
        
        # Reconstruct filename with cleaned components
        safe_filename = f"{safe_base}{safe_ext}"
        
        # If the filename is empty after cleaning, use a default
        if not safe_filename.strip('_.- '):
            safe_filename = 'document'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = Path(upload_folder) / f"{safe_filename}_{timestamp}.json"
        
        # Prepare document data
        document = {
            'id': str(file_path.stem),
            'filename': str(file_path.name),
            'path': str(file_path),
            'uploaded_at': datetime.now().isoformat(),
            'metadata': metadata,
            'content': content
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
            
        return str(file_path)
        
    except Exception as e:
        error_msg = f"Error saving document: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
