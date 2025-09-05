from typing import List

def format_result(text: str, query_terms: List[str], max_length: int = 300) -> str:
    """Format search result to show context around query terms."""
    if len(text) <= max_length:
        return text
        
    lower_text = text.lower()
    best_score = -1
    best_start = 0
    
    for start in range(0, len(text) - max_length, max_length // 2):
        window = lower_text[start:start + max_length]
        score = sum(1 for term in query_terms if term.lower() in window)
        if score > best_score:
            best_score = score
            best_start = start
    
    result = text[best_start:best_start + max_length]
    if best_start > 0:
        result = '...' + result
    if best_start + max_length < len(text):
        result = result + '...'
        
    return result
