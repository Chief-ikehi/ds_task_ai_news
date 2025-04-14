import faiss
import numpy as np
from typing import List, Dict, Tuple
from config import settings

class VectorStore:
    def __init__(self):
        self.dimension = settings.VECTOR_DIMENSION
        self.index = faiss.IndexFlatL2(self.dimension)
        self.article_ids = []
        
    def add_articles(self, article_embeddings: Dict[str, List[float]]):
        """Add article embeddings to the vector store"""
        embeddings = []
        for article_id, embedding in article_embeddings.items():
            embeddings.append(embedding)
            self.article_ids.append(article_id)
            
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
    
    def search_similar(self, query_embedding: List[float], k: int = 5) -> List[str]:
        """Search for similar articles using a query embedding"""
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, k)
        
        # Return the article IDs of the similar articles
        return [self.article_ids[idx] for idx in indices[0]]
    
    def clear(self):
        """Clear the vector store"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.article_ids = []