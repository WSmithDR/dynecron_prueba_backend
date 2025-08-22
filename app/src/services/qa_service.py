import logging
from typing import Dict, List, Any, Tuple
from ..services.search_service import search_service
from ..models.qa_models import QAResponse, AnswerCitation
from ..exceptions.qa_exceptions import NoDocumentsLoadedError, AnswerGenerationError
from ..utils.qa_utils import (
    check_documents_exist, 
    generate_answer_with_llm, 
    create_citations, 
    extract_keywords,
    clean_response
)


# Configurar logger
logger = logging.getLogger(__name__)


async def answer_question(question: str) -> QAResponse:
    try:
        # Verificar que hay documentos en el directorio
        if not check_documents_exist():
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
        llm_response = await generate_answer_with_llm(question, context)
        
        # Extraer las palabras clave y limpiar la respuesta
        keywords = extract_keywords(llm_response)
        answer_text = clean_response(llm_response)
        
        logger.info(f"Respuesta generada para: {question}")
        logger.info(f"Respuesta: {answer_text}")
        logger.info(f"Palabras clave extraídas: {keywords}")
        
        # Crear un formato de resultados de búsqueda compatible con la función de citas
        search_results = {
            'results': [
                {
                    'text': doc['content'],
                    'documentName': doc['source'],
                    'relevanceScore': 1.0  # Puntuación máxima ya que son los documentos completos
                }
                for doc in unique_docs.values()
            ]
        }
        
        # Generar citas mejoradas usando las palabras clave
        citations = create_citations(search_results, keywords)
        logger.info(f"Generadas {len(citations)} citas usando {len(keywords)} palabras clave")
        
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