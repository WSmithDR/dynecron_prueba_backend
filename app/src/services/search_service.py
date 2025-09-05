"""Functional search service for document retrieval."""
import os
import re
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config.settings import UPLOAD_DIR, SEARCH_CONFIG
from ..utils.text_utils import clean_text, split_into_chunks

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
SearchResult = Dict[str, Any]
DocumentChunk = Dict[str, Any]
SearchState = Dict[str, Any]

# Global state
_state = {
    'documents': [],
    'doc_metadata': [],
    'tfidf_matrix': None,
    'vectorizer': TfidfVectorizer(
        token_pattern=r'(?u)\b\w[\w-]*\w\b',
        ngram_range=(1, 2),
        max_features=SEARCH_CONFIG["max_results"],
        strip_accents='unicode',
        lowercase=True
    )
}

def process_content(content: str) -> List[str]:
    """Process content into clean, meaningful chunks."""
    cleaned = clean_text(content).lower()
    return split_into_chunks(cleaned)

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

def load_all_documents(data_folder: Path = UPLOAD_DIR) -> None:
    """Load and index all documents from the data folder."""
    data_folder = Path(data_folder)
    data_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== Loading documents from: {data_folder.absolute()} ===")
    print(f"Directory exists: {data_folder.exists()}")
    print(f"Directory contents: {list(data_folder.glob('*'))}")
    
    all_chunks = []
    all_metadata = []
    
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            file_path = data_folder / filename
            chunks = load_document(file_path)
            all_chunks.extend(chunk['text'] for chunk in chunks)
            all_metadata.extend(chunks)
    
    if all_chunks:
        print(f"\nFound {len(all_chunks)} document chunks to index")
        tfidf_matrix = _state['vectorizer'].fit_transform(all_chunks)
        _state.update({
            'documents': all_chunks,
            'doc_metadata': all_metadata,
            'tfidf_matrix': tfidf_matrix
        })
        print(f"TF-IDF matrix created with shape: {tfidf_matrix.shape}")
    else:
        print("\nNo valid document chunks found to index")

def format_result(text: str, query_terms: List[str], max_length: int = 300) -> str:
    """Format search result to show context around query terms."""
    if len(text) <= max_length:
        return text
        
    lower_text = text.lower()
    best_score = -1
    best_start = 0
    
    for start in range(0, len(text) - max_length, max_length // 2):
        window = lower_text[start:start + max_length]
        score = sum(1 for term in query_terms if term.lower() in window)
        if score > best_score:
            best_score = score
            best_start = start
    
    result = text[best_start:best_start + max_length]
    if best_start > 0:
        result = '...' + result
    if best_start + max_length < len(text):
        result = result + '...'
        
    return result

async def search(query: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Search for relevant passages in the documents with pagination."""
    if not query.strip() or not _state['documents'] or _state['tfidf_matrix'] is None:
        return empty_result(page, page_size)
    
    try:
        query = query.strip().lower()
        query_terms = re.findall(r'\b[\w-]+\b', query, re.UNICODE)
        
        if not query_terms:
            return empty_result(page, page_size)
        
        query_vec = _state['vectorizer'].transform([query])
        similarities = cosine_similarity(query_vec, _state['tfidf_matrix']).flatten()
        
        valid_indices = [i for i, score in enumerate(similarities) if score > 0]
        if not valid_indices:
            return empty_result(page, page_size)
            
        # Sort by score in descending order
        sorted_indices = sorted(valid_indices, key=lambda i: -similarities[i])
        total_results = len(sorted_indices)
        total_pages = (total_results + page_size - 1) // page_size
        
        # Get paginated results
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_indices = sorted_indices[start_idx:end_idx]
        
        results = [
            format_search_result(idx, similarities, query_terms, _state['doc_metadata'])
            for idx in page_indices
        ]
        
        # Format results to match the expected API response
        formatted_results = [{
            'text': r['text'],
            'documentName': r['document_name'],
            'relevanceScore': r['score'],
            'document_id': r['document_id'],
            'chunk_index': r['chunk_index']
        } for r in results]
        
        return {
            'results': formatted_results,
            'total': total_results,
            'page': page,
            'pageSize': page_size,  # Match the frontend's expected casing
            'totalPages': total_pages  # Match the frontend's expected casing
        }
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return empty_result(page, page_size)

def format_search_result(idx: int, similarities: np.ndarray, 
                       query_terms: List[str], metadata: List[Dict]) -> Dict[str, Any]:
    """Format a single search result."""
    meta = metadata[idx]
    formatted_text = format_result(meta['text'], query_terms)
    
    return {
        'document_id': meta['document_id'],
        'document_name': meta['document_name'],
        'score': float(similarities[idx]),
        'text': formatted_text,
        'full_text': meta['text'],
        'chunk_index': meta['chunk_index']
    }

def empty_result(page: int, page_size: int) -> SearchResult:
    """Return an empty search result."""
    return {
        'results': [],
        'total': 0,
        'page': page,
        'page_size': page_size,
        'total_pages': 0
    }

# Initialize the search service on import
load_all_documents()
