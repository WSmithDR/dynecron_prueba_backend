import os
import json
import PyPDF2
import io
import tempfile
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException, status

class FileService:
    """
    Servicio para el procesamiento de archivos (PDF y TXT).
    Maneja la extracción de texto y el guardado de documentos.
    """
    
    def __init__(self, upload_folder: str = "data"):
        """
        Inicializa el servicio de archivos.
        
        Args:
            upload_folder: Directorio donde se guardarán los archivos procesados
        """
        self.upload_folder = upload_folder
        self.ALLOWED_EXTENSIONS = {"pdf", "txt"}
        self.MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
        self.CHUNK_SIZE = 1024 * 1024  # 1MB
        
        # Asegurar que el directorio de carga existe
        os.makedirs(upload_folder, exist_ok=True)
    
    def extract_text_from_pdf(self, content: bytes) -> str:
        """
        Extrae texto de un archivo PDF.
        
        Args:
            content: Contenido binario del PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_parts = []
            
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"Advertencia: Error al extraer texto de una página: {str(e)}")
                    continue
            
            return "\n\n".join(text_parts).strip()
            
        except Exception as e:
            error_msg = f"Error al extraer texto del PDF: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)
    
    def save_document(self, metadata: Dict[str, Any], content: str) -> str:
        """
        Guarda un documento procesado en formato JSON.
        
        Args:
            metadata: Metadatos del documento
            content: Contenido del documento
            
        Returns:
            str: Ruta del archivo guardado
        """
        # Crear un nombre de archivo único
        base_name = f"{metadata['fecha_creacion']}_{metadata['nombre_original']}"
        file_name = f"{os.path.splitext(base_name)[0]}.json"
        file_path = os.path.join(self.upload_folder, file_name)
        
        # Crear el documento estructurado
        document = {
            "metadata": metadata,
            "contenido": content,
            "fecha_procesamiento": datetime.now(timezone.utc).isoformat()
        }
        
        # Guardar como JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    async def process_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Procesa un archivo subido a través de FastAPI UploadFile.
        
        Args:
            file: Archivo subido a través de FastAPI
            
        Returns:
            Dict con el resultado del procesamiento
        """
        # Validar extensión
        if not self._is_extension_allowed(file.filename or ''):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Formatos aceptados: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
            
        temp_file = None
        try:
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_size = 0
            
            # Leer el archivo en chunks
            while True:
                chunk = await file.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                    
                file_size += len(chunk)
                if file_size > self.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"El archivo {file.filename} excede el tamaño máximo permitido de {self.MAX_FILE_SIZE/1024/1024}MB"
                    )
                temp_file.write(chunk)
            
            # Procesar el archivo
            temp_file.seek(0)
            with open(temp_file.name, 'rb') as f:
                file_content = f.read()
            
            # Procesar según la extensión
            extension = os.path.splitext(file.filename or 'file')[1].lower()
            if extension == '.pdf':
                content_text = self.extract_text_from_pdf(file_content)
            elif extension == '.txt':
                content_text = file_content.decode('utf-8')
            else:
                raise ValueError(f"Formato de archivo no soportado: {extension}")
            
            # Crear metadatos
            metadata = {
                'nombre_original': file.filename or 'archivo_sin_nombre',
                'tipo_contenido': file.content_type or 'application/octet-stream',
                'tamano_bytes': file_size,
                'fecha_creacion': datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                'extension': extension,
                'num_caracteres': len(content_text)
            }
            
            # Guardar el documento
            file_path = self.save_document(metadata, content_text)
            
            # Asegurar que todos los campos requeridos estén presentes
            return {
                "procesado_exitoso": True,
                "archivo": file.filename or 'archivo_sin_nombre',
                "ruta": file_path,
                "tamano_bytes": file_size,
                "tipo": file.content_type or 'application/octet-stream',
                "num_caracteres": len(content_text),
                "nombre_original": file.filename or 'archivo_sin_nombre',
                "extension": extension,
                "contenido": content_text[:500]  # Solo primeros 500 caracteres para depuración
            }
            
        except HTTPException:
            raise
        except Exception as e:
            return {
                "procesado_exitoso": False,
                "archivo": file.filename or 'archivo_desconocido',
                "error": str(e)
            }
        finally:
            # Limpiar archivo temporal
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
    
    def _is_extension_allowed(self, filename: str) -> bool:
        """Verifica si la extensión del archivo está permitida."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
