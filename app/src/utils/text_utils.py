import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text for better search and display"""
    # Remove email and URLs
    text = re.sub(r'\S+@\S+|http\S+|www\.\S+', '', text)
    # Keep only letters, numbers, and basic punctuation
    text = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ.,;:!?¿¡-]', ' ', text)
    # Collapse whitespace
    return ' '.join(text.split())

def split_into_chunks(text: str, sentences_per_chunk: int = 2) -> List[str]:
    """Split text into chunks of sentences"""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Group into chunks
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = ' '.join(sentences[i:i + sentences_per_chunk])
        if len(chunk) > 20:  # Skip very short chunks
            chunks.append(chunk)
    
    return chunks or [text]  # Fallback to full text if no chunks created
