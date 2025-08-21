from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import Awaitable, Dict, Any, Optional
import logging

from app.src.models.qa_models import QAResponse, QARequest, AnswerCitation
from ..services.qa_service import answer_question, NoDocumentsLoadedError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

qa_controller = APIRouter()

@qa_controller.post(
    "",
    response_model=QAResponse,
    summary="Answer a question",
    description="Generate an answer to a question based on the uploaded documents"
)
async def answer_question_endpoint(question_data: QARequest) -> QAResponse:
    """
    Endpoint para responder preguntas basadas en los documentos cargados.
    
    Args:
        question_data: Datos de la pregunta a responder
        
    Returns:
        QAResponse: Respuesta a la pregunta con referencias a las fuentes
    """
    try:
        # Validar que se proporcionó una pregunta
        if not question_data.question.strip():
            return QAResponse(
                answer="La pregunta no puede estar vacía.",
                citations=[],
                hasEnoughContext=False,
                question=question_data.question
            )
        
        # Llamar al servicio de QA para generar una respuesta
        logger.info(f"Procesando pregunta: {question_data.question}")
        response = await answer_question(question_data.question)
        
        # Registrar respuesta exitosa
        logger.info(f"Respuesta generada para: {question_data.question}")
        
        return response
        
    except NoDocumentsLoadedError as ndle:
        logger.warning(str(ndle))
        return QAResponse(
            answer=str(ndle),
            citations=[],
            hasEnoughContext=False,
            question=getattr(question_data, 'question', '')
        )
    except Exception as e:
        # Log the full error with traceback
        error_msg = f"Error procesando la pregunta: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return QAResponse(
            answer=error_msg,
            citations=[],
            hasEnoughContext=False,
            question=getattr(question_data, 'question', '')
        )
