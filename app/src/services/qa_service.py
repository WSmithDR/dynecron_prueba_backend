import logging
from typing import Dict, List, Any
from ..services.search_service import search_service
from ..models.qa_models import QAResponse, AnswerCitation
from ..exceptions.qa_exceptions import NoDocumentsLoadedError, AnswerGenerationError
from ..utils.qa_utils import check_documents_exist, generate_answer_with_llm


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
        answer_text = await generate_answer_with_llm(question, context)
        
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