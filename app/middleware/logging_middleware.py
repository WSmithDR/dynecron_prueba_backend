"""
Logging middleware for the FastAPI application.
Handles request logging and error handling.
"""
import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

# Configuración de logging
logger = logging.getLogger(__name__)

async def log_requests_middleware(request: Request, call_next):
    """
    Middleware para logging de peticiones y manejo de errores.
    
    Args:
        request: Incoming request
        call_next: Next middleware or route handler
        
    Returns:
        Response from the next middleware/route or error response
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - "
            f"{process_time:.2f}ms"
        )
        return response
    except Exception as e:
        logger.error(f"Error in request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
