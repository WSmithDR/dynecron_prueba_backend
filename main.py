from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.src.routes.file_upload import router as upload_router

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
    max_age=3600,
)

# Middleware para compresión de respuestas
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuración para manejo de archivos grandes
app.router.default_max_request_size = 1024 * 1024 * 1024  # 1GB

# Include routers
app.include_router(upload_router, prefix="/api", tags=["file-upload"])

@app.get("/")
async def root():
    return {"message": "¡Hola, mundo!"}