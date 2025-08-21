"""
Módulo para excepciones personalizadas del servicio de QA.
"""
import logging
from typing import Optional

# Configurar logger
exceptions_logger = logging.getLogger(__name__)

class QAServiceError(Exception):
    """Clase base para excepciones del servicio de QA."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
        # Registrar el error
        log_message = f"{self.__class__.__name__}: {message}"
        if details:
            log_message += f"\nDetalles: {details}"
        exceptions_logger.error(log_message, exc_info=True)

class NoDocumentsLoadedError(QAServiceError):
    """Excepción lanzada cuando no hay documentos cargados en el sistema."""
    def __init__(self, message: str = "No hay documentos cargados en el sistema.", details: Optional[dict] = None):
        super().__init__(
            message=message,
            details={
                "suggested_action": "Por favor, carga documentos antes de hacer preguntas.",
                "error_code": "NO_DOCUMENTS_LOADED",
                **(details or {})
            }
        )

class DocumentProcessingError(QAServiceError):
    """Excepción lanzada cuando ocurre un error al procesar un documento."""
    def __init__(self, document_name: str, error: Exception):
        super().__init__(
            message=f"Error al procesar el documento: {document_name}",
            details={
                "document": document_name,
                "error": str(error),
                "error_type": error.__class__.__name__
            }
        )

class AnswerGenerationError(QAServiceError):
    """Excepción lanzada cuando falla la generación de una respuesta."""
    def __init__(self, question: str, error: Exception):
        super().__init__(
            message=f"Error al generar respuesta para: {question}",
            details={
                "question": question,
                "error": str(error),
                "error_type": error.__class__.__name__
            }
        )
