from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.src.routes.file_upload import router as upload_router
from app.src.routes.search import router as search_router

# Configuración para manejar archivos grandes (1GB)
app = FastAPI(
    title="API de Procesamiento de Documentos",
    description="API para procesar documentos PDF y TXT",
    version="1.0.0",
    # Aumentar el límite de tamaño de carga a 1GB
    max_upload_size=1024 * 1024 * 1024,  # 1GB
    debug=True
)

# Configuración de middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplaza con la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Asegura que todos los encabezados estén expuestos
    max_age=3600,
)

# Middleware para compresión de respuestas
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuración para manejo de archivos grandes
app.router.default_max_request_size = 1024 * 1024 * 1024  # 1GB

# Middleware para manejar CORS en respuestas de error
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
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
        logger.error(f"Error in request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

# Include routers
app.include_router(upload_router, prefix="/api", tags=["file-upload"])
app.include_router(search_router, prefix="/api", tags=["search"])

@app.get("/")
async def root():
    return {"message": "¡Hola, mundo!"}