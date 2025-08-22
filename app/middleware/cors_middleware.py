from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors_middleware(app: FastAPI):
    """
    Configure CORS middleware to allow any origin.
    WARNING: Only use this in development. In production, specify allowed origins.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
        expose_headers=["*"],
        max_age=600,  # 10 minutes
    )
