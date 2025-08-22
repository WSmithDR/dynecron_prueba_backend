import logging
from typing import List, Dict, Any, Optional
from app.src.models.qa_models import AnswerCitation

logger = logging.getLogger(__name__)

def find_best_matching_snippet(text: str, keywords: List[str]) -> str:
    """
    Encuentra el mejor fragmento de texto que contenga la mayoría de las palabras clave.
    
    Args:
        text: Texto completo a analizar
        keywords: Lista de palabras clave para buscar en el texto
        
    Returns:
        str: El fragmento de texto más relevante que contiene las palabras clave
    """
    if not text or not keywords:
        return text[:500] if text else ""
    
    # Convertir a minúsculas para búsqueda sin distinción de mayúsculas
    text_lower = text.lower()
    keywords_lower = [kw.lower() for kw in keywords if kw]
    
    # Contar ocurrencias de palabras clave
    keyword_count = {}
    for kw in keywords_lower:
        keyword_count[kw] = text_lower.count(kw)
    
    # Ordenar palabras clave por frecuencia
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    
    # Tomar las 3 palabras clave más frecuentes
    top_keywords = [kw for kw, _ in sorted_keywords[:3]]
    
    # Encontrar posiciones de las palabras clave
    positions = []
    for kw in top_keywords:
        start = 0
        while True:
            pos = text_lower.find(kw, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(kw)))
            start = pos + 1
    
    if not positions:
        return text[:500]  # Devolver inicio si no se encuentran palabras clave
    
    # Encontrar el rango que cubre la mayoría de las palabras clave
    positions.sort()
    window_start = positions[0][0]
    window_end = positions[0][1]
    best_window = (window_start, window_end)
    max_keywords = 1
    
    for i in range(1, len(positions)):
        current_start, current_end = positions[i]
        window_start = min(window_start, current_start)
        window_end = max(window_end, current_end)
        
        # Si la ventana es demasiado grande, ajustar
        if window_end - window_start > 1000:  # Máximo 1000 caracteres
            window_start = current_start
            window_end = current_end
        
        current_keywords = sum(1 for start, end in positions 
                             if window_start <= start and end <= window_end)
        
        if current_keywords > max_keywords:
            max_keywords = current_keywords
            best_window = (window_start, window_end)
    
    # Extraer el mejor fragmento con un poco de contexto
    start = max(0, best_window[0] - 50)
    end = min(len(text), best_window[1] + 50)
    
    # Asegurar que no cortemos palabras a la mitad
    while start > 0 and text[start] not in ' \t\n':
        start -= 1
    while end < len(text) and text[end] not in ' \t\n':
        end += 1
    
    snippet = text[start:end].strip()
    
    # Resaltar las palabras clave en el snippet
    for kw in keywords:
        if kw.lower() in text_lower:
            snippet = snippet.replace(kw, f'**{kw}**')
    
    return snippet

def create_citations(search_results: Dict[str, Any], keywords: Optional[List[str]] = None) -> List[AnswerCitation]:
    """
    Crea una lista de citas a partir de los resultados de búsqueda, mejoradas con las palabras clave.
    
    Args:
        search_results: Resultados de búsqueda del servicio de búsqueda
        keywords: Lista de palabras clave para mejorar la relevancia de las citas
        
    Returns:
        List[AnswerCitation]: Lista de citas formateadas y mejoradas
    """
    if not keywords:
        keywords = []
    
    citations = []
    seen_sources = set()
    
    for result in search_results.get('results', []):
        content = result.get('text', '')
        source = result.get('documentName', 'Documento desconocido')
        
        # Evitar duplicados
        if source in seen_sources:
            continue
            
        seen_sources.add(source)
        
        # Mejorar el fragmento de texto basado en palabras clave
        improved_content = find_best_matching_snippet(content, keywords) if keywords else content[:500]
        
        citation = AnswerCitation(
            source=source,
            content=improved_content,
            score=result.get('relevanceScore')
        )
        citations.append(citation)
        
        # Limitar el número de citas
        if len(citations) >= 3:  # Máximo 3 citas
            break
            
    logger.debug(f"Generadas {len(citations)} citas con {len(keywords)} palabras clave")
    return citations
