from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio

from ..services.file_service import FileService

# Inicializar el servicio de archivos
file_service = FileService(upload_folder="data")

router = APIRouter()


@router.post("/ingest")
async def procesar_archivos(files: List[UploadFile] = File(...)):
    """
    Endpoint para procesar múltiples archivos.
    
    Args:
        files: Lista de archivos a procesar
        
    Returns:
        JSON con los resultados del procesamiento
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se han proporcionado archivos para procesar"
        )
    
    # Procesar archivos en paralelo
    resultados = await asyncio.gather(
        *(file_service.process_uploaded_file(archivo) for archivo in files),
        return_exceptions=True
    )
    
    # Separar resultados exitosos y fallidos
    archivos_procesados = []
    errores = []
    
    for resultado in resultados:
        if isinstance(resultado, Exception):
            errores.append({
                "archivo": "archivo_desconocido",
                "error": str(resultado)
            })
        elif resultado.get("procesado_exitoso", False):
            archivos_procesados.append({
                "archivo": resultado["archivo"],
                "ruta": resultado["ruta"],
                "tamano_bytes": resultado["tamano_bytes"],
                "tipo": resultado["tipo"],
                "num_caracteres": resultado["num_caracteres"]
            })
        else:
            errores.append({
                "archivo": resultado.get("archivo", "archivo_desconocido"),
                "error": resultado.get("error", "Error desconocido")
            })
    
    # Asegurarse de que todos los campos requeridos estén presentes
    response = {
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
    
    # Agregar encabezados CORS si es necesario
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    return JSONResponse(content=response, headers=headers)
