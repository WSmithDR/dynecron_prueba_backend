from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timezone
import json
import PyPDF2
import io
import asyncio
import tempfile
import shutil
from pathlib import Path

# Configuración para archivos grandes
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
CHUNK_SIZE = 1024 * 1024  # 1MB por chunk

router = APIRouter()

# Directorios
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSIONES_PERMITIDAS = {"pdf", "txt"}

def es_extension_permitida(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

def extraer_texto_pdf(contenido: bytes) -> str:
    """
    Extrae el texto de un archivo PDF sin procesamiento adicional.
    Devuelve el contenido en texto plano.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contenido))
        texto_completo = []
        
        # Extraer texto de cada página
        for pagina in pdf_reader.pages:
            try:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo.append(texto_pagina)
            except Exception as e:
                print(f"Advertencia: Error al extraer texto de una página: {str(e)}")
                continue
        
        # Unir todas las páginas con doble salto de línea
        return "\n\n".join(texto_completo).strip()
        
    except Exception as e:
        error_msg = f"Error al extraer texto del PDF: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg)

def guardar_documento(metadata: Dict[str, Any], contenido: str) -> str:
    """
    Guarda el documento procesado en formato JSON.
    
    Args:
        metadata: Diccionario con metadatos del documento
        contenido: Contenido del documento a guardar
        
    Returns:
        str: Ruta completa del archivo guardado
    """
    # Asegurarse de que el directorio de destino exista
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Crear un nombre de archivo único
    nombre_base = f"{metadata['fecha_creacion']}_{metadata['nombre_original']}"
    nombre_archivo = f"{os.path.splitext(nombre_base)[0]}.json"
    ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    
    # Crear el documento estructurado
    documento = {
        "metadata": metadata,
        "contenido": contenido,
        "fecha_procesamiento": datetime.now(timezone.utc).isoformat()
    }
    
    # Guardar como JSON
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(documento, f, ensure_ascii=False, indent=2)
    
    return ruta_archivo

async def procesar_archivo(archivo: UploadFile) -> Dict[str, Any]:
    """
    Procesa un único archivo (PDF o TXT) y devuelve su contenido procesado.
    
    Args:
        archivo: Archivo a procesar (UploadFile)
        
    Returns:
        Dict con los metadatos y contenido del archivo
    """
    temp_file = None
    try:
        # Validar tipo de archivo
        if not es_extension_permitida(archivo.filename):
            raise ValueError(f"Tipo de archivo no permitido. Formatos aceptados: {', '.join(EXTENSIONES_PERMITIDAS)}")
            
        # Crear un archivo temporal para el contenido
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo.filename)[1])
        
        # Leer el archivo en chunks y validar tamaño
        size = 0
        while True:
            chunk = await archivo.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                raise ValueError(f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE/1024/1024}MB")
            temp_file.write(chunk)
        
        # Cerrar el archivo temporal para poder leerlo
        temp_file.close()
        
        # Leer el contenido del archivo temporal
        with open(temp_file.name, 'rb') as f:
            contenido = f.read()
        
        # Determinar el tipo de archivo
        extension = os.path.splitext(archivo.filename)[1].lower()
        
        # Procesar según la extensión
        if extension == '.pdf':
            contenido_texto = extraer_texto_pdf(contenido)
        else:  # .txt
            contenido_texto = contenido.decode('utf-8')
        
        # Crear metadatos
        metadata = {
            'nombre_original': archivo.filename,
            'tipo_contenido': archivo.content_type or 'application/octet-stream',
            'tamano_bytes': len(contenido),
            'fecha_creacion': datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
            'extension': extension,
            'num_caracteres': len(contenido_texto)
        }
        
        # Guardar el documento
        ruta_guardado = guardar_documento(metadata, contenido_texto)
        
        return {
            'estado': 'procesado',
            'archivo': archivo.filename,
            'ruta': ruta_guardado,
            'metadata': metadata
        }
        
    except Exception as e:
        return {
            'estado': 'error',
            'archivo': archivo.filename,
            'error': str(e)
        }
    finally:
        # Limpiar archivo temporal si existe
        try:
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        except Exception as e:
            print(f"Error al limpiar archivo temporal: {e}")

@router.post("/ingest")
async def procesar_archivos(files: List[UploadFile] = File(...)):
    """
    Endpoint para procesar múltiples archivos (PDF y TXT).
    
    Args:
        files: Lista de archivos a procesar
        
    Returns:
        Dict con los resultados del procesamiento
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se han proporcionado archivos para procesar"
        )
    
    # Procesar archivos en paralelo
    tareas = [procesar_archivo(file) for file in files]
    resultados = await asyncio.gather(*tareas, return_exceptions=True)
    
    # Procesar resultados
    archivos_procesados = []
    errores = []
    
    for resultado in resultados:
        if isinstance(resultado, Exception):
            errores.append({
                'archivo': 'Desconocido',
                'error': str(resultado)
            })
        elif resultado.get('estado') == 'error':
            errores.append({
                'archivo': resultado.get('archivo', 'Desconocido'),
                'error': resultado.get('error', 'Error desconocido')
            })
        else:
            archivos_procesados.append({
                'archivo': resultado['archivo'],
                'ruta': resultado['ruta'],
                'tamano_bytes': resultado['metadata']['tamano_bytes'],
                'tipo': resultado['metadata']['tipo_contenido']
            })
    
    return {
        'archivos_procesados': archivos_procesados,
        'errores': errores,
        'total_procesados': len(archivos_procesados),
        'total_errores': len(errores)
    }
