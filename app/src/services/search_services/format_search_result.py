

def format_search_result(idx: int, similarities: np.ndarray, 
                       query_terms: List[str], metadata: List[Dict]) -> Dict[str, Any]:
    """Format a single search result."""
    meta = metadata[idx]
    formatted_text = format_result(meta['text'], query_terms)
    
    return {
        'document_id': meta['document_id'],
        'document_name': meta['document_name'],
        'score': float(similarities[idx]),
        'text': formatted_text,
        'full_text': meta['text'],
        'chunk_index': meta['chunk_index']
    }
