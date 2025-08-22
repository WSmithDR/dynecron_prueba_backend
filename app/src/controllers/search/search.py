from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional

from ...services.search_service import search
from ...models.search import PaginatedSearchResponse, SearchResult

search_router = APIRouter(tags=["search"])

@search_router.get(
    "",
    response_model=PaginatedSearchResponse,
    summary="Search documents",
    description="Search for relevant passages in the uploaded documents with pagination"
)
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    pageSize: Optional[int] = None  # For backward compatibility
) -> PaginatedSearchResponse:
    # Use limit parameter if provided, otherwise use pageSize for backward compatibility
    page_size = limit if pageSize is None else pageSize
    """
    Search for relevant passages in the documents with pagination
    
    - **q**: Search query (minimum 2 characters)
    - **page**: Page number (starts at 1)
    - **pageSize**: Number of results per page (1-100)
    """
    try:
        # Call the search service with the correct parameter name
        results = await search(
            query=q,
            page=page,
            page_size=page_size
        )
        
        # Ensure the response matches the PaginatedSearchResponse model with camelCase field names
        return {
            "results": results.get("results", []),
            "total": results.get("total", 0),
            "page": page,
            "pageSize": page_size,  # Using camelCase to match the model
            "totalPages": (results.get("total", 0) + page_size - 1) // page_size  # Using camelCase
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )
