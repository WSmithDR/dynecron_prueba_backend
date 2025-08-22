from fastapi import APIRouter
from datetime import datetime
import platform
from typing import Dict, Any

from ...models.search import SearchStatus
from ...services.search_service import _state

# Create router for status endpoints
status_router = APIRouter(tags=["search"])

@status_router.get(
    "/status",
    response_model=SearchStatus,
    summary="Get search service status",
    description="Get the current status of the search service"
)
async def get_search_status() -> Dict[str, Any]:
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
        doc_count = len(_state.get('documents', []))
        
        # Create status response
        return SearchStatus(
            status="ready",  # Default status
            documents_loaded=doc_count,
            last_updated=datetime.now(),
            device=device_info
        )
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "documents_loaded": 0,
            "last_updated": datetime.now(),
            "device": platform.node()
        }
