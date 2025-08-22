"""Client utilities for QA service."""
import os
from openai import OpenAI

# Module-level client instance
_client = None

def get_client() -> OpenAI:
    """Get or initialize the OpenAI client with Hugging Face's inference API."""
    global _client
    if _client is None:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN no está configurado en las variables de entorno")
            
        _client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
    return _client
