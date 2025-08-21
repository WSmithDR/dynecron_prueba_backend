from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import logging
from pathlib import Path

from ..config.settings import UPLOAD_DIR, SEARCH_CONFIG
from ..services.search_service import search_service
from ..models.qa_models import QAResponse, AnswerCitation
from ..exceptions.qa_exceptions import (
    NoDocumentsLoadedError, 
    AnswerGenerationError,
    DocumentProcessingError
)

# Configurar logger
logger = logging.getLogger(__name__)


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

async def _generate_answer_with_llm(question: str, context: List[Dict[str, Any]]) -> str:
    """
    Genera una respuesta usando el contexto proporcionado.
    Esta es una implementación simulada que puede reemplazarse con una llamada real a un LLM.
    """
    if not context:
        return "No encuentro esa información en los documentos cargados."

    # Simulamos una operación asíncrona
    await asyncio.sleep(0.1)
    
    # En una implementación real, esto llamaría a una API de LLM de forma asíncrona
    sources = list(set([doc['source'] for doc in context]))
    source_references = ", ".join(f"[Fuente {i+1}]" for i in range(len(sources)))
    
    return (
        f"Basado en la información disponible: {context[0]['content'][:150]}... "
        f"{source_references}. "
        "(Nota: Esta es una respuesta de demostración. En producción, se usaría un modelo de lenguaje real.)"
    )

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
    Responde una pregunta basándose en los documentos disponibles.
    
    Args:
        question: La pregunta a responder
        
    Returns:
        QAResponse: La respuesta generada con metadatos y citas
        
    Raises:
        NoDocumentsLoadedError: Si no hay documentos cargados en el sistema
        AnswerGenerationError: Si hay un error al generar la respuesta
    """
    try:
        # Verificar que hay documentos en el directorio
        if not _check_documents_exist():
            raise NoDocumentsLoadedError()
            
        logger.info(f"Procesando pregunta: {question}")
        
        # Asegurarse de que el índice esté actualizado
        search_service.reload_documents()
        
        # Buscar pasajes relevantes
        search_results = search_service.search(question, page=1, page_size=3)
        
        # Verificar si hay resultados
        if not search_results or not search_results.get('results'):
            return "No encuentro suficiente información en los documentos cargados para responder a tu pregunta."
        
        # Filtrar resultados por puntuación de confianza
        relevant_results = [
            result for result in search_results['results']
            if result.get('relevanceScore', 0) >= SEARCH_CONFIG['min_confidence']
        ]
        
        # Crear citas para los resultados relevantes
        citations = _create_citations({'results': relevant_results})
        
        # Formatear contexto para el LLM
        context = []
        
        for result in relevant_results:
            context.append({
                'content': result.get('text', ''),
                'source': result.get('documentName', 'Documento desconocido')
            })
        
        # Generar respuesta usando el contexto
        answer_text = await _generate_answer_with_llm(question, context)
        
        # Si no hay contexto relevante, devolver un mensaje predeterminado
        if not context:
            answer_text = "No encuentro esa información en los documentos cargados."
        
        sources = list(set([doc['source'] for doc in context if 'source' in doc]))
        return QAResponse(
            answer=answer_text + _format_sources(sources),
            citations=citations,
            hasEnoughContext=len(context) > 0,
            question=question
        )
            
    except NoDocumentsLoadedError as ndle:
        # Este error ya está registrado en la clase de excepción
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