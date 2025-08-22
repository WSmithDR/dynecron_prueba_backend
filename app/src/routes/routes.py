

from fastapi import APIRouter

from ..controllers.file_upload import file_upload_controller
from ..controllers.search import router as search_router
from ..controllers.qa import qa_controller

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(file_upload_controller, prefix="/ingest", tags=["file-upload"])
api_router.include_router(search_router, prefix="", tags=["search"])
api_router.include_router(qa_controller, prefix="/ask", tags=["qa"])
