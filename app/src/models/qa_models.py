from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QARequest(BaseModel):
    """Modelo para la solicitud de respuesta a preguntas.
    
    Attributes:
        question (str): La pregunta que se desea responder.
    """
    question: str = Field(..., description="La pregunta que se desea responder")


class AnswerCitation(BaseModel):
    """Modelo para las citas de las respuestas.
    
    Attributes:
        source (str): La fuente de la cita (nombre del documento).
        content (str): El contenido citado.
        page (int, optional): Número de página si está disponible.
        score (float, optional): Puntuación de relevancia de la cita.
    """
    source: str = Field(..., description="Nombre del documento fuente")
    content: str = Field(..., description="Texto relevante de la fuente")
    page: Optional[int] = Field(None, description="Número de página si está disponible")
    score: Optional[float] = Field(None, description="Puntuación de relevancia")


class QAResponse(BaseModel):
    """Modelo para la respuesta del servicio de preguntas y respuestas.
    
    Attributes:
        answer (str): La respuesta generada.
        citations (List[AnswerCitation]): Lista de citas que respaldan la respuesta.
        hasEnoughContext (bool): Indica si se encontró suficiente contexto.
        timestamp (datetime): Fecha y hora de la respuesta.
        question (str, optional): Pregunta original.
    """
    answer: str = Field(..., description="La respuesta generada")
    citations: List[AnswerCitation] = Field(default_factory=list, description="Lista de citas")
    hasEnoughContext: bool = Field(True, description="Indica si hay suficiente contexto")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de la respuesta")
    question: Optional[str] = Field(None, description="Pregunta original")


class QADocument(BaseModel):
    """Modelo para los documentos procesados por el QA.
    
    Attributes:
        id (str): Identificador único del documento.
        name (str): Nombre del documento.
        content (str): Contenido del documento.
        metadata (Dict[str, Any]): Metadatos adicionales.
        created_at (datetime): Fecha de creación.
    """
    id: str
    name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: str
    content: str
    page: Optional[int] = None

class QAResponse(BaseModel):
    """Modelo para la respuesta a preguntas.
    
    Attributes:
        answer (str): La respuesta generada a la pregunta.
        citations (List[AnswerCitation]): Lista de citas de los documentos.
        hasEnoughContext (bool): Indica si hay suficiente contexto para responder.
    """
    answer: str
    citations: List[AnswerCitation] = []
    hasEnoughContext: bool = True
