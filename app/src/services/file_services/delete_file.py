import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def safe_json_load(file_path: Path) -> Optional[Dict]:
    """Safely load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in {file_path.name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path.name}: {str(e)}")
        return None

def find_file_by_metadata(upload_path: Path, file_id: str) -> Optional[Path]:
    """Find a file by checking its metadata."""
    for file_path in upload_path.glob('*'):
        if file_path.suffix == '.json':
            file_data = safe_json_load(file_path)
            if file_data and (file_data.get('id') == file_id or 
                            file_data.get('filename', '').startswith(file_id) or
                            file_path.stem == file_id):
                return file_path
    return None

def delete_file(upload_folder: str, file_id: str) -> Dict[str, Any]:
    """
    Delete a file from the upload directory.
    
    Args:
        upload_folder: Path to the upload directory
        file_id: ID or name of the file to delete (with or without .json extension)
        
    Returns:
        Dict with operation result
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: For other errors during deletion
    """
    try:
        logger.info(f"Starting delete_file for file_id: {file_id}")
        upload_path = Path(upload_folder)
        
        if not upload_path.exists():
            error_msg = f"Upload directory does not exist: {upload_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # Log directory contents for debugging
        files_in_dir = list(upload_path.glob('*'))
        logger.info(f"Files in {upload_path}: {[f.name for f in files_in_dir]}")
        
        # Try to find the file by metadata first
        file_path = find_file_by_metadata(upload_path, file_id)
        if file_path:
            logger.info(f"Found file by metadata match: {file_path}")
            try:
                file_path.unlink()
                return {
                    'success': True,
                    'message': f'File {file_id} deleted successfully',
                    'file_id': file_id,
                    'deleted_path': str(file_path)
                }
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {str(e)}")
                raise
        
        # If not found by ID, try direct filename match
        possible_paths = [
            upload_path / f"{file_id}.json",  # Add .json if not present
            upload_path / file_id,             # Try as is
            upload_path / f"{file_id}"         # Try without any extension
        ]
        
        # Remove duplicate paths while preserving order
        possible_paths = list(dict.fromkeys(possible_paths))
        
        file_path = None
        for path in possible_paths:
            if path.exists():
                file_path = path
                break
                
        if not file_path or not file_path.exists():
            error_msg = f"File not found: {file_id}. Tried paths: {[str(p) for p in possible_paths]}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        logger.info(f"Deleting file: {file_path}")
        os.remove(file_path)
        
        # Verify deletion
        if file_path.exists():
            error_msg = f"File deletion failed: {file_path} still exists"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        result = {
            'success': True,
            'message': f'File {file_id} deleted successfully',
            'file_id': file_id,
            'deleted_path': str(file_path)
        }
        
        logger.info(f"Successfully deleted file: {result}")
        return result
        
    except FileNotFoundError as e:
        logger.error(f"File not found error in delete_file: {str(e)}")
        raise
    except PermissionError as e:
        error_msg = f"Permission denied when trying to delete {file_id}: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n\n{traceback.format_exc()}"
        logger.error(f"Unexpected error in delete_file: {error_details}")
        raise Exception(f"Error deleting file {file_id}: {str(e)}")
