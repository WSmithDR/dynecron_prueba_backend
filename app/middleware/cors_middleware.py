"""
CORS middleware configuration for the FastAPI application.
Handles Cross-Origin Resource Sharing (CORS) settings.
"""
from fastapi.middleware.cors import CORSMiddleware

def setup_cors_middleware(app):
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

async def add_cors_headers_middleware(request, call_next):
    """
    Middleware to add CORS headers to responses.
    
    Args:
        request: Incoming request
        call_next: Next middleware or route handler
        
    Returns:
        Response with CORS headers
    """
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
