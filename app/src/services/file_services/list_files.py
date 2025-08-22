import json
import aiofiles
import os
from pathlib import Path
from typing import List, Dict, Any

async def list_uploaded_files(upload_folder: str) -> List[Dict[str, Any]]:
    try:
        files = []
        upload_path = Path(upload_folder)
        
        # Ensure the directory exists
        if not upload_path.exists():
            return []
            
        # Scan for JSON files
        for file_path in upload_path.glob('*.json'):
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    file_data = json.loads(content)
                    
                # Map to frontend's expected structure
                metadata = file_data.get('metadata', {})
                file_info = {
                    'id': file_data.get('id', file_path.stem),
                    'name': file_data.get('filename', file_path.name),  # Frontend expects 'name'
                    'path': str(file_path),
                    'upload_date': file_data.get('uploaded_at'),  # Frontend expects 'upload_date'
                    'content_type': metadata.get('content_type', 'application/octet-stream'),
                    'size': metadata.get('file_size', 0),  # Frontend expects 'size'
                    'num_characters': len(file_data.get('content', '')),  # Frontend expects 'num_characters'
                    'metadata': metadata
                }
                files.append(file_info)
                
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"Error reading file {file_path}: {str(e)}")
                continue
                
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
        
        return files
        
    except Exception as e:
        error_msg = f"Error listing files: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
