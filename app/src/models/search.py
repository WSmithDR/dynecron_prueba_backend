
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime


class SearchResult(BaseModel):
    """Model for search results"""
    text: str = Field(..., description="Relevant text snippet")
    document_name: str = Field(..., alias="documentName", description="Name of the source document")
    relevance_score: float = Field(..., alias="relevanceScore", ge=0, le=1, description="Relevance score between 0 and 1")
    
    class Config:
        allow_population_by_field_name = True

class SearchStatus(BaseModel):
    """Model for search service status"""
    status: Literal["ready", "indexing", "error"]
    documents_loaded: int
    last_updated: Optional[datetime] = None
    device: str = Field(..., description="Device/Server where the service is running")
    error: Optional[str] = None


class PaginatedSearchResponse(BaseModel):
    """Model for paginated search response"""
    results: List[SearchResult]
    total: int
    page: int
    pageSize: int
    totalPages: int
