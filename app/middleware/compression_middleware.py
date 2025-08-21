"""
Compression middleware for the FastAPI application.
Handles response compression using GZIP.
"""
from fastapi.middleware.gzip import GZipMiddleware

def setup_gzip_middleware(app):
    """
    Configure GZIP compression middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(GZipMiddleware, minimum_size=1000)
