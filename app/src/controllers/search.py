from fastapi import APIRouter, Query, HTTPException, status
from datetime import datetime
import platform
from ..services.search_service import search, load_all_documents
from ..models.search import SearchStatus, PaginatedSearchResponse

search_controller = APIRouter()

@search_controller.get(
    "",
    response_model=PaginatedSearchResponse,
    summary="Search documents",
    description="Search for relevant passages in the uploaded documents with pagination"
)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=100, description="Number of results per page")
) -> Dict[str, Any]:
    """
    Search for relevant passages in the documents with pagination
    
    - **q**: Search query (minimum 2 characters)
    - **page**: Page number (starts at 1)
    - **pageSize**: Number of results per page (1-100)
    """
    try:
        # Call the search function directly with pagination parameters
        response = await search(q, page, pageSize)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )

@search_controller.get(
    "/status",
    response_model=SearchStatus,
    summary="Get search service status",
    description="Get the current status of the search service"
)
async def get_search_status():
    """
    Get the current status of the search service including:
    - Current status (ready/indexing/error)
    - Number of documents loaded
    - Last update timestamp
    - Device information
    """
    try:
        # Get basic system information
        device_info = f"{platform.node()} ({platform.system()} {platform.release()})"
        
        # Get document count from the search module
        from ..services.search_service import _state
        doc_count = len(_state.get('documents', []))
        
        # Create status response
        status = SearchStatus(
            status="ready",  # Default status
            documents_loaded=doc_count,
            last_updated=datetime.now(),
            device=device_info
        )
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting search status: {str(e)}"
        )
