
"""
Search-related Pydantic models.

This module contains all Pydantic models related to search functionality.
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

class SearchResult(BaseModel):
    """Model for individual search results."""
    text: str = Field(..., description="Relevant text snippet")
    document_name: str = Field(
        ..., 
        alias="documentName", 
        description="Name of the source document"
    )
    relevance_score: float = Field(
        ..., 
        alias="relevanceScore", 
        ge=0, 
        le=1, 
        description="Relevance score between 0 and 1"
    )
    document_id: str = Field(
        ...,
        description="Unique identifier for the source document"
    )
    chunk_index: int = Field(
        ...,
        description="Index of the chunk in the document"
    )
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "text": "This is a relevant text snippet.",
                "documentName": "document.pdf",
                "relevanceScore": 0.95,
                "document_id": "doc123",
                "chunk_index": 1
            }
        }

class SearchStatus(BaseModel):
    """Model for search service status."""
    status: Literal["ready", "indexing", "error"] = Field(
        ...,
        description="Current status of the search service"
    )
    documents_loaded: int = Field(
        ...,
        ge=0,
        description="Number of documents currently loaded in the search index"
    )
    last_updated: datetime = Field(
        ...,
        description="Timestamp of when the search index was last updated"
    )
    device: str = Field(
        ...,
        description="Information about the device running the search service"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if status is 'error'"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "ready",
                "documents_loaded": 5,
                "last_updated": "2023-01-01T00:00:00Z",
                "device": "server-01 (Linux 5.4.0)",
                "error": None
            }
        }

class PaginatedSearchResponse(BaseModel):
    """Model for paginated search response."""
    results: List[Dict[str, Any]] = Field(
        ...,
        description="List of search results with document information"
    )
    total: int = Field(
        ...,
        description="Total number of results across all pages"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number"
    )
    pageSize: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of results per page"
    )
    totalPages: int = Field(
        ...,
        ge=0,
        description="Total number of pages available"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "text": "Sample text",
                        "documentName": "document.pdf",
                        "relevanceScore": 0.95,
                        "document_id": "doc123",
                        "chunk_index": 1
                    }
                ],
                "total": 10,
                "page": 1,
                "pageSize": 10,
                "totalPages": 1
            }
        }
