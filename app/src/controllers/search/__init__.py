from fastapi import APIRouter
from .search import search_router
from .status import status_router

# Create main router for search endpoints
router = APIRouter(prefix="", tags=["search"])

# Include all search-related routers with their own prefixes
router.include_router(search_router, prefix="/search")
router.include_router(status_router, prefix="/search/status")

# Export the main router
__all__ = ["router"]
