from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import asyncio
import logging

from ..services.file_service import FileService
from ..services.search_service import load_all_documents as reload_search_index

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router without prefix (will be added in routes.py)
file_upload_controller = APIRouter()

def get_file_service():
    """Dependency for getting file service instance"""
    return FileService(upload_folder="data")

@file_upload_controller.post("/")
async def procesar_archivos(
    files: List[UploadFile] = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """
    Endpoint para procesar múltiples archivos.
    
    Args:
        files: Lista de archivos a procesar
        file_service: Injected file service instance
        
    Returns:
        JSON con los resultados del procesamiento
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se han proporcionado archivos para procesar"
        )
    
    try:
        # Procesar archivos en paralelo
        tasks = [file_service.process_uploaded_file(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        archivos_procesados = []
        errores = []
        
        # Verificar si se procesó al menos un archivo correctamente
        any_success = False
        
        for file, result in zip(files, results):
            if isinstance(result, Exception):
                errores.append({
                    "archivo": file.filename,
                    "error": str(result)
                })
            elif result.get("procesado_exitoso", False):
                archivos_procesados.append({
                    "archivo": result["archivo"],
                    "ruta": result["ruta"],
                    "tamano_bytes": result["tamano_bytes"],
                    "tipo": result["tipo"],
                    "num_caracteres": result["num_caracteres"]
                })
                any_success = True
            else:
                errores.append({
                    "archivo": result.get("archivo", file.filename),
                    "error": result.get("error", "Error desconocido")
                })
        
        # Si se procesó al menos un archivo correctamente, recargar el índice de búsqueda
        if any_success:
            try:
                reload_search_index()
                logger.info("Índice de búsqueda actualizado correctamente")
            except Exception as e:
                logger.error(f"Error al actualizar el índice de búsqueda: {str(e)}")
                errores.append({
                    'archivo': 'Sistema',
                    'error': f'Error al actualizar el índice de búsqueda: {str(e)}'
                })
        
        # Construir respuesta
        response = {
            'mensaje': 'Procesamiento completado',
            'archivos_procesados': [{
                'archivo': p['archivo'],
                'ruta': p['ruta'],
                'tamano_bytes': p['tamano_bytes'],
                'tipo': p.get('tipo', 'application/octet-stream'),
                'num_caracteres': p.get('num_caracteres', 0)
            } for p in archivos_procesados],
            'errores': [{
                'archivo': e.get('archivo', 'archivo_desconocido'),
                'error': str(e.get('error', 'Error desconocido'))
            } for e in errores],
            'total_procesados': len(archivos_procesados),
            'total_errores': len(errores)
        }
        
        # Agregar encabezados CORS
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        return JSONResponse(content=response, status_code=status.HTTP_200_OK, headers=headers)
    
    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el procesamiento: {str(e)}"
        )

@file_upload_controller.get("/files", response_model=List[Dict[str, Any]])
async def listar_archivos(
    file_service: FileService = Depends(get_file_service)
):
    """
    Endpoint para listar todos los archivos subidos.
    
    Returns:
        Lista de archivos con sus metadatos
    """
    try:
        files = await file_service.list_uploaded_files()
        return files
    except Exception as e:
        logger.error(f"Error al listar archivos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar archivos: {str(e)}"
        )

@file_upload_controller.delete("/files/{file_id}")
async def eliminar_archivo(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Endpoint para eliminar un archivo específico.
    
    Args:
        file_id: ID del archivo a eliminar
        
    Returns:
        Resultado de la operación
    """
    try:
        result = await file_service.delete_file(file_id)
        # Recargar el índice de búsqueda después de eliminar
        try:
            reload_search_index()
        except Exception as e:
            logger.warning(f"No se pudo actualizar el índice de búsqueda: {str(e)}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar archivo {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el archivo: {str(e)}"
        )

@file_upload_controller.delete("/files")
async def eliminar_todos_los_archivos(
    confirm: bool = Query(..., description="Debe ser True para confirmar la eliminación"),
    file_service: FileService = Depends(get_file_service)
):
    """
    Endpoint para eliminar todos los archivos subidos.
    
    Args:
        confirm: Debe ser True para confirmar la eliminación
        
    Returns:
        Resultado de la operación
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere confirmación para eliminar todos los archivos"
        )
        
    try:
        result = await file_service.delete_all_files()
        # Recargar el índice de búsqueda después de eliminar
        try:
            reload_search_index()
        except Exception as e:
            logger.warning(f"No se pudo actualizar el índice de búsqueda: {str(e)}")
            
        return result
    except Exception as e:
        logger.error(f"Error al eliminar todos los archivos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar los archivos: {str(e)}"
        )