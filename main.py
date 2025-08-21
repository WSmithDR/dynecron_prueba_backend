from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.src.routes.file_upload import router as upload_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix="/api", tags=["file-upload"])

@app.get("/")
async def root():
    return {"message": "¡Hola, mundo!"}