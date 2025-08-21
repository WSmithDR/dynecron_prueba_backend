import os
import re
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..config.settings import UPLOAD_DIR, SEARCH_CONFIG
from ..utils.text_utils import clean_text, split_into_chunks

class SearchService:
    def __init__(self, data_folder: Path = UPLOAD_DIR):
        """Initialize the search service with the specified data folder.
        
        Args:
            data_folder: Path to the directory containing document data
        """
        self.data_folder = Path(data_folder)
        # Using custom token pattern to better handle Spanish words with accents
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w[\w-]*\w\b',
            ngram_range=(1, 2),
            max_features=SEARCH_CONFIG["max_results"],
            strip_accents='unicode',
            lowercase=True
        )
        self.documents = []
        self.doc_metadata = []
        self.tfidf_matrix = None
    
    def _process_content(self, content: str) -> List[str]:
        """Process content into clean, meaningful chunks"""
        # Clean the content first
        cleaned = clean_text(content)
        # Normalize unicode characters and lowercase for better matching
        cleaned = cleaned.lower()
        # Split into sentence-based chunks
        return split_into_chunks(cleaned)

    def reload_documents(self):
        """Clear and reload all documents from the data folder"""
        self.documents = []
        self.doc_metadata = []
        self.load_documents()
        
    def load_documents(self):
        """Load and index all documents from the data folder"""
        # Ensure the data directory exists
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Debug: Log the data folder path and its contents
        print(f"\n=== Loading documents from: {self.data_folder.absolute()} ===")
        print(f"Directory exists: {self.data_folder.exists()}")
        print(f"Directory contents: {list(self.data_folder.glob('*'))}")
        
        if not any(self.data_folder.iterdir()):
            print("No files found in data directory")
            return
            
        for filename in os.listdir(self.data_folder):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.data_folder, filename)
                    print(f"\nProcessing file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"Loaded JSON data from {filename}")
                    
                    # Process content into clean chunks
                    content = data.get('contenido', '')
                    chunks = self._process_content(content)
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk) < 20:  # Skip very short chunks
                            continue
                            
                        self.documents.append(chunk)
                        self.doc_metadata.append({
                            'document_id': filename,
                            'document_name': data.get('metadata', {}).get('nombre_original', filename),
                            'chunk_index': i,
                            'text': chunk
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        if self.documents:
            print(f"\nFound {len(self.documents)} document chunks to index")
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            print(f"TF-IDF matrix created with shape: {self.tfidf_matrix.shape}")
        else:
            print("\nNo valid document chunks found to index")
    
    def _format_result(self, text: str, query_terms: List[str], max_length: int = 300) -> str:
        """Format search result to show context around query terms"""
        # The text is already cleaned and chunked, just ensure it's not too long
        if len(text) <= max_length:
            return text
            
        # Find the best window containing the most query terms
        lower_text = text.lower()
        best_score = -1
        best_start = 0
        
        # Try different starting positions
        for start in range(0, len(text) - max_length, max_length // 2):
            window = lower_text[start:start + max_length]
            score = sum(1 for term in query_terms if term.lower() in window)
            
            if score > best_score:
                best_score = score
                best_start = start
        
        # Extract the best window
        result = text[best_start:best_start + max_length]
        
        # Add ellipsis if we're not at the start/end
        if best_start > 0:
            result = '...' + result
        if best_start + max_length < len(text):
            result = result + '...'
            
        return result
    
    def search(self, query: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Search for relevant passages in the documents with pagination
        
        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of results per page
            
        Returns:
            Dictionary containing:
            - results: List of search results
            - total: Total number of results
            - page: Current page number
            - page_size: Number of results per page
            - total_pages: Total number of pages
        """
        if not query.strip():
            return {
                'results': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
            
        if not self.documents or self.tfidf_matrix is None:
            return {
                'results': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
            
        try:
            # Preprocess query - normalize and clean
            query = query.strip().lower()
            # Normalize unicode characters and split into terms
            query_terms = re.findall(r'\b[\w-]+\b', query, re.UNICODE)
            # If no valid terms after processing, return empty results
            if not query_terms:
                return {
                    'results': [],
                    'total': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0
                }
            
            # Transform query to TF-IDF vector
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarity for all documents
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get all results with similarity > 0, sorted by score (descending)
            valid_indices = [i for i, score in enumerate(similarities) if score > 0]
            valid_scores = [float(similarities[i]) for i in valid_indices]
            
            # Sort by score in descending order
            sorted_indices = [i for _, i in sorted(zip(valid_scores, valid_indices), reverse=True)]
            total_results = len(sorted_indices)
            total_pages = (total_results + page_size - 1) // page_size
            
            # Calculate pagination bounds
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_indices = sorted_indices[start_idx:end_idx]
            
            results = []
            for idx in page_indices:
                score = float(similarities[idx])
                meta = self.doc_metadata[idx]
                
                # Format the text to show context around query terms
                formatted_text = self._format_result(meta['text'], query_terms)
                
                results.append({
                    'text': formatted_text,
                    'documentName': meta['document_name'],  # Changed to match frontend
                    'relevanceScore': round(score, 4)  # Changed to camelCase for frontend
                })
            
            return {
                'results': results,
                'total': total_results,
                'page': page,
                'pageSize': page_size,  # camelCase for consistency
                'totalPages': total_pages  # camelCase for consistency
            }
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return {
                'results': [],
                'total': 0,
                'page': page,
                'pageSize': page_size,
                'totalPages': 0,
                'error': str(e)
            }

# Singleton instance
search_service = SearchService()
search_service.load_documents()
