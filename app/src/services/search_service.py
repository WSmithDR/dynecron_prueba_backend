import os
import json
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SearchService:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.documents = []
        self.doc_metadata = []
        self.tfidf_matrix = None
    
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
                    
                    # Split content into paragraphs
                    content = data.get('contenido', '')
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                    
                    for i, para in enumerate(paragraphs):
                        self.documents.append(para)
                        self.doc_metadata.append({
                            'document_id': filename,
                            'document_name': data.get('metadata', {}).get('nombre_original', filename),
                            'chunk_index': i,
                            'text': para
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        # Create TF-IDF matrix
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant passages"""
        if not self.documents or self.tfidf_matrix is None:
            return []
            
        # Transform query to TF-IDF vector
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top K results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include relevant results
                meta = self.doc_metadata[idx]
                results.append({
                    'text': meta['text'],
                    'document_name': meta['document_name'],
                    'relevance_score': float(similarities[idx])
                })
        
        return results

# Singleton instance
search_service = SearchService()
search_service.load_documents()
