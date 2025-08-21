import re
import unicodedata
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text for better search and display"""
    if not text:
        return ""
        
    # Convert to string if not already
    text = str(text)
    
    # Remove email and URLs
    text = re.sub(r'\S+@\S+|http\S+|www\.\S+', '', text)
    
    # Normalize unicode characters (convert accented characters to their base form)
    text = unicodedata.normalize('NFKD', text)
    
    # Keep only letters, numbers, and basic punctuation
    text = re.sub(r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ.,;:!?¿¡-]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def split_into_chunks(text: str, sentences_per_chunk: int = 2) -> List[str]:
    """Split text into chunks of sentences"""
    if not text:
        return []
        
    # Split into sentences - handle multiple sentence terminators
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Group into chunks
    chunks = []
    current_chunk = []
    
    for sentence in sentences:
        current_chunk.append(sentence)
        if len(current_chunk) >= sentences_per_chunk:
            chunk = ' '.join(current_chunk)
            chunks.append(chunk)
            current_chunk = []
    
    # Add any remaining sentences as a chunk
    if current_chunk:
        chunk = ' '.join(current_chunk)
        chunks.append(chunk)
    
    # Ensure we have at least one chunk
    if not chunks and text.strip():
        chunks = [text.strip()]
    
    # Filter out very short chunks (less than 20 chars)
    chunks = [chunk for chunk in chunks if len(chunk) >= 20]
    
    return chunks
