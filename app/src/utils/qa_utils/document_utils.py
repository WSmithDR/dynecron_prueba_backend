import logging
from pathlib import Path
from app.src.config.settings import UPLOAD_DIR

logger = logging.getLogger(__name__)

def check_documents_exist() -> bool:
    """
    Verifica si hay documentos en el directorio de carga.
    
    Returns:
        bool: True si hay al menos un archivo .json en el directorio, False en caso contrario
    """
    try:
        # Verificar si el directorio existe
        if not UPLOAD_DIR.exists() or not UPLOAD_DIR.is_dir():
            return False
            
        # Contar archivos .json en el directorio
        json_files = list(UPLOAD_DIR.glob('*.json'))
        return len(json_files) > 0
        
    except Exception as e:
        error_msg = f"Error al verificar archivos en {UPLOAD_DIR}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False
