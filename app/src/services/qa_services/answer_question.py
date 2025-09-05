import logging
from ..services.search_service import _state as search_state
from ..models.qa_models import QAResponse
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
        doc_metadata = search_state.get('doc_metadata', [])
        if not doc_metadata:
            return QAResponse(
                answer="No hay documentos cargados en el sistema.",
                citations=[],
                hasEnoughContext=False,
                question=question
            )
        
        # Obtener el contenido completo de todos los documentos únicos
        unique_docs = {}
        for doc in doc_metadata:
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
        
        # Crear un formato de resultados de búsqueda con metadatos completos para citas
        search_results = {
            'results': [
                {
                    'text': doc.get('content', ''),
                    'documentName': doc.get('source', 'Documento'),
                    'document_id': doc_id,  # Incluir el ID del documento
                    'chunk_index': doc.get('chunk_index', 0),  # Incluir índice del chunk
                    'relevanceScore': 1.0,  # Puntuación máxima ya que son los documentos completos
                    'metadata': {
                        'source': doc.get('source', ''),
                        'document_id': doc_id,
                        'chunk_index': doc.get('chunk_index', 0)
                    }
                }
                for doc_id, doc in unique_docs.items()
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