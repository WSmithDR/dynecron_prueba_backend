

from fastapi import APIRouter

from ..controllers.file_upload import file_upload_controller
from ..controllers.search import search_controller

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(file_upload_controller, prefix="/ingest", tags=["file-upload"])
api_router.include_router(search_controller, prefix="/search", tags=["search"])
