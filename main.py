from fastapi import FastAPI
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar middlewares
from app.middleware.cors_middleware import setup_cors_middleware
from app.middleware.compression_middleware import setup_gzip_middleware
from app.middleware.logging_middleware import log_requests_middleware

# Importar routers
from app.src.routes.routes import api_router

# Configuración para manejar archivos grandes (1GB)
app = FastAPI(
    title="API de Procesamiento de Documentos",
    description="API para procesar documentos PDF y TXT",
    version="1.0.0"
)

# Configuración para manejo de archivos grandes
app.router.default_max_request_size = 1024 * 1024 * 1024  # 1GB

# Configuración de middlewares
setup_cors_middleware(app)  # Debe ir primero
setup_gzip_middleware(app)
app.middleware("http")(log_requests_middleware)

# Incluir rutas de la API
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "¡Hola, mundo!"}