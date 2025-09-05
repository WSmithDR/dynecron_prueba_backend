from ..models.search_models import SearchResult

def empty_result(page: int, page_size: int) -> SearchResult:
    """Return an empty search result."""
    return {
        'results': [],
        'total': 0,
        'page': page,
        'page_size': page_size,
        'total_pages': 0
    }
