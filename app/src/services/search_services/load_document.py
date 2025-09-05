from ..utils.text_utils import process_content
from pathlib import Path
import json
from typing import List

def load_document(file_path: Path) -> List[DocumentChunk]:
    """Load and process a single document file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get('contenido', '')
        chunks = process_content(content)
        
        return [
            {
                'document_id': file_path.name,
                'document_name': data.get('metadata', {}).get('nombre_original', file_path.name),
                'chunk_index': i,
                'text': chunk
            }
            for i, chunk in enumerate(chunks)
            if len(chunk) >= 20  # Skip very short chunks
        ]
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return []
