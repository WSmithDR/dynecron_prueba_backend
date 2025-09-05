from empy_result import empty_result
from format_search_result import format_search_result
from ..models.search_models import SearchResult
from sklearn.metrics.pairwise import cosine_similarity
import re
from ..constants import _state

async def search(query: str, page: int = 1, page_size: int = 10) -> SearchResult:
    """Search for relevant passages in the documents with pagination."""
    if not query.strip() or not _state['documents'] or _state['tfidf_matrix'] is None:
        return empty_result(page, page_size)
    
    try:
        query = query.strip().lower()
        query_terms = re.findall(r'\b[\w-]+\b', query, re.UNICODE)
        
        if not query_terms:
            return empty_result(page, page_size)
        
        query_vec = _state['vectorizer'].transform([query])
        similarities = cosine_similarity(query_vec, _state['tfidf_matrix']).flatten()
        
        valid_indices = [i for i, score in enumerate(similarities) if score > 0]
        if not valid_indices:
            return empty_result(page, page_size)
            
        # Sort by score in descending order
        sorted_indices = sorted(valid_indices, key=lambda i: -similarities[i])
        total_results = len(sorted_indices)
        total_pages = (total_results + page_size - 1) // page_size
        
        # Get paginated results
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_indices = sorted_indices[start_idx:end_idx]
        
        results = [
            format_search_result(idx, similarities, query_terms, _state['doc_metadata'])
            for idx in page_indices
        ]
        
        # Format results to match the expected API response
        formatted_results = [{
            'text': r['text'],
            'documentName': r['document_name'],
            'relevanceScore': r['score'],
            'document_id': r['document_id'],
            'chunk_index': r['chunk_index']
        } for r in results]
        
        return {
            'results': formatted_results,
            'total': total_results,
            'page': page,
            'pageSize': page_size,  # Match the frontend's expected casing
            'totalPages': total_pages  # Match the frontend's expected casing
        }
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return empty_result(page, page_size)
