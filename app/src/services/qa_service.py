from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from openai import OpenAI
from dotenv import load_dotenv

from ..config.settings import UPLOAD_DIR, SEARCH_CONFIG
from ..services.search_service import search_service
from ..models.qa_models import QAResponse, AnswerCitation
from ..exceptions.qa_exceptions import (
    NoDocumentsLoadedError, 
    AnswerGenerationError,
    DocumentProcessingError
)

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
_client = None

def _check_documents_exist() -> bool:
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

def _get_client() -> OpenAI:
    """Get or initialize the OpenAI client with Hugging Face's inference API."""
    global _client
    if _client is None:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN no está configurado en las variables de entorno")
            
        _client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
    return _client

def _format_json_for_prompt(data: Any, indent: int = 0) -> str:
    """Formatea datos JSON para mostrarlos en el prompt."""
    if isinstance(data, dict):
        return '\n'.join([
            f"{'  ' * indent}{key} ({type(value).__name__}): {_format_json_for_prompt(value, indent + 1)}"
            for key, value in data.items()
        ])
    elif isinstance(data, list):
        return '\n'.join([
            f"{'  ' * indent}- {_format_json_for_prompt(item, indent + 1)}"
            for item in data
        ])
    else:
        return str(data)

async def _generate_answer_with_llm(question: str, context: List[Dict[str, Any]]) -> str:
    """
    Genera una respuesta basada en los datos proporcionados usando el modelo de Hugging Face.
    
    Args:
        question: La pregunta sobre los datos
        context: Lista de documentos JSON
        
    Returns:
        str: Respuesta generada por el modelo de lenguaje
    """
    if not context:
        return "No encuentro información en los documentos cargados."

    try:
        # Tomar el primer documento del contexto
        json_data = context[0].get('content', {})
        
        # Formatear los datos JSON para el prompt
        formatted_data = _format_json_for_prompt(json_data)
        
        # Crear el mensaje para el modelo
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente útil que responde preguntas basándose en los datos proporcionados."
            },
            {
                "role": "user",
                "content": f"""Analiza los siguientes datos y responde la pregunta de manera concisa.
                
Datos:
{formatted_data}

Pregunta: {question}

Respuesta:"""
            }
        ]
        
        # Obtener el cliente de OpenAI configurado para Hugging Face
        client = _get_client()
        
        # Realizar la petición a la API
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:fireworks-ai",
            messages=messages,
            max_tokens=300,
            temperature=0.1,
            top_p=0.9
        )
        
        # Extraer y retornar la respuesta
        answer = completion.choices[0].message.content.strip()
        return answer if answer else "No encontré información específica sobre eso en los datos."
        
    except Exception as e:
        logger.error(f"Error al generar respuesta: {str(e)}", exc_info=True)
        return "No pude procesar la solicitud en este momento. Por favor, intenta con otra pregunta."

def _format_sources(sources: List[str]) -> str:
    """Formatea la información de fuentes para la respuesta."""
    if not sources:
        return ""
    return "\n\nFuentes:\n" + "\n".join(f"- {source}" for source in sources)

def _check_documents_loaded() -> None:
    """
    Función obsoleta. Se mantiene por compatibilidad.
    La verificación de documentos ahora se hace directamente en answer_question
    """
    pass

def _create_citations(search_results: Dict[str, Any]) -> List[AnswerCitation]:
    """Crea una lista de citas a partir de los resultados de búsqueda."""
    citations = []
    for result in search_results.get('results', []):
        citation = AnswerCitation(
            source=result.get('documentName', 'Documento desconocido'),
            content=result.get('text', ''),
            score=result.get('relevanceScore')
        )
        citations.append(citation)
    return citations


async def answer_question(question: str) -> QAResponse:
    """
    Responde una pregunta usando el modelo de lenguaje con el contenido completo de los documentos.
    
    Args:
        question: La pregunta a responder
        
    Returns:
        QAResponse: La respuesta generada con metadatos
        
    Raises:
        NoDocumentsLoadedError: Si no hay documentos cargados en el sistema
        AnswerGenerationError: Si hay un error al generar la respuesta
    """
    try:
        # Verificar que hay documentos en el directorio
        if not _check_documents_exist():
            raise NoDocumentsLoadedError()
            
        logger.info(f"Procesando pregunta: {question}")
        
        # Obtener todos los documentos del servicio de búsqueda
        if not hasattr(search_service, 'doc_metadata') or not search_service.doc_metadata:
            return QAResponse(
                answer="No hay documentos cargados en el sistema.",
                citations=[],
                hasEnoughContext=False,
                question=question
            )
        
        # Obtener el contenido completo de todos los documentos únicos
        unique_docs = {}
        for doc in search_service.doc_metadata:
            doc_id = doc.get('document_id')
            if doc_id not in unique_docs:
                unique_docs[doc_id] = {
                    'content': doc.get('text', ''),
                    'source': doc.get('document_name', 'Documento desconocido')
                }
        
        if not unique_docs:
            return QAResponse(
                answer="No hay contenido disponible en los documentos cargados.",
                citations=[],
                hasEnoughContext=False,
                question=question
            )
        
        # Crear lista de contextos con contenido completo de cada documento
        context = list(unique_docs.values())
        
        # Generar respuesta usando el LLM con todo el contenido
        answer_text = await _generate_answer_with_llm(question, context)
        
        # Crear citas para los documentos usados como contexto
        citations = []
        for doc in list(unique_docs.values())[:3]:  # Limitar a 3 documentos como referencia
            citations.append(AnswerCitation(
                source=doc['source'],
                content=doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                page=None,
                score=1.0
            ))
        
        return QAResponse(
            answer=answer_text,
            citations=citations,
            hasEnoughContext=len(context) > 0,
            question=question
        )
            
    except NoDocumentsLoadedError as ndle:
        return QAResponse(
            answer=str(ndle),
            citations=[],
            hasEnoughContext=False,
            question=question
        )
    except Exception as e:
        # Registrar y envolver el error en una excepción más específica
        error = AnswerGenerationError(question, e)
        return QAResponse(
            answer=f"Error al procesar la pregunta: {error.message}",
            citations=[],
            hasEnoughContext=False,
            question=question
        )