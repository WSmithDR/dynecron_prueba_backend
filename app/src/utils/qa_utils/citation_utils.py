"""Citation-related utilities for QA service."""
from typing import List, Dict, Any
from app.src.models.qa_models import AnswerCitation

def create_citations(search_results: Dict[str, Any]) -> List[AnswerCitation]:
    """
    Crea una lista de citas a partir de los resultados de búsqueda.
    
    Args:
        search_results: Resultados de búsqueda del servicio de búsqueda
        
    Returns:
        List[AnswerCitation]: Lista de citas formateadas
    """
    citations = []
    for result in search_results.get('results', []):
        citation = AnswerCitation(
            source=result.get('documentName', 'Documento desconocido'),
            content=result.get('text', ''),
            score=result.get('relevanceScore')
        )
        citations.append(citation)
    return citations
