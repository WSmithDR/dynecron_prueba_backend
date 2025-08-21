from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..services.search_service import search_service

router = APIRouter()

class SearchResult(BaseModel):
    """Model for search results"""
    text: str = Field(..., description="Relevant text snippet")
    document_name: str = Field(..., description="Name of the source document")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score between 0 and 1")

@router.get(
    "/search",
    response_model=List[SearchResult],
    summary="Search documents",
    description="Search for relevant passages in the uploaded documents"
)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results to return")
):
    """
    Search for relevant passages in the documents
    
    - **q**: Search query (minimum 2 characters)
    - **limit**: Number of results to return (1-20)
    """
    try:
        results = search_service.search(q, limit)
        if not results:
            return []
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )
