import os
import json
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..utils.text_utils import clean_text, split_into_chunks

class SearchService:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=10000
        )
        self.documents = []
        self.doc_metadata = []
        self.tfidf_matrix = None
    
    def _process_content(self, content: str) -> List[str]:
        """Process content into clean, meaningful chunks"""
        # Clean the content first
        cleaned = clean_text(content)
        # Split into sentence-based chunks
        return split_into_chunks(cleaned)

    def load_documents(self):
        """Load and index all documents from the data folder"""
        self.documents = []
        self.doc_metadata = []
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder, exist_ok=True)
            return
            
        for filename in os.listdir(self.data_folder):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.data_folder, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
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
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
    
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
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant passages in the documents
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            
        Returns:
            List of dictionaries containing:
            - text: The relevant text snippet
            - document_name: Name of the source document
            - relevance_score: Float between 0 and 1 indicating match quality
        """
        if not query.strip():
            return []
            
        if not self.documents or self.tfidf_matrix is None:
            return []
            
        try:
            # Preprocess query
            query = query.strip()
            query_terms = query.lower().split()
            
            # Transform query to TF-IDF vector
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top K results with similarity > 0
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score <= 0:
                    continue
                    
                meta = self.doc_metadata[idx]
                
                # Format the text to show context around query terms
                formatted_text = self._format_result(meta['text'], query_terms)
                
                results.append({
                    'text': formatted_text,
                    'document_name': meta['document_name'],
                    'relevance_score': round(score, 4)  # Round to 4 decimal places
                })
                
                # If we have enough high-quality results, return early
                if len(results) >= top_k:
                    break
                    
            return results
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return []

# Singleton instance
search_service = SearchService()
search_service.load_documents()
