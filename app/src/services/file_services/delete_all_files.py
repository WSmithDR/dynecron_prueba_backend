import os
from pathlib import Path
from typing import Dict, Any

def delete_all_files(upload_folder: str, confirm: bool = False) -> Dict[str, Any]:
    try:
        if not confirm:
            raise ValueError("Confirmation required. Set confirm=True to delete all files.")
            
        upload_path = Path(upload_folder)
        
        # Check if directory exists
        if not upload_path.exists():
            return {
                'success': True,
                'message': 'No files to delete',
                'deleted_count': 0
            }
            
        # Count files before deletion
        file_count = len(list(upload_path.glob('*.json')))
        
        if file_count == 0:
            return {
                'success': True,
                'message': 'No files to delete',
                'deleted_count': 0
            }
            
        # Remove all JSON files
        for file_path in upload_path.glob('*.json'):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")
                continue
                
        return {
            'success': True,
            'message': f'Successfully deleted {file_count} files',
            'deleted_count': file_count
        }
        
    except ValueError:
        raise
    except Exception as e:
        error_msg = f"Error deleting files: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
