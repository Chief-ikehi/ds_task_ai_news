import cohere
from typing import List, Dict
from config import settings

class EmbeddingGenerator:
    def __init__(self):
        self.co = cohere.Client(api_key=settings.COHERE_API_KEY)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Cohere's API"""
        try:
            response = self.co.embed(
                texts=texts,
                model='embed-english-v3.0',
                input_type='search_document'
            )
            return response.embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_article_embeddings(self, articles: List[Dict]) -> Dict[str, List[float]]:
        """Generate embeddings for articles and return a dictionary mapping article IDs to embeddings"""
        # Combine title and content for better semantic representation
        texts = [f"{article['title']} {article['content']}" for article in articles]
        
        # Generate embeddings for all texts
        embeddings = self.generate_embeddings(texts)
        
        # Create a mapping of article IDs to their embeddings
        return {articles[i]['id']: embeddings[i] for i in range(len(articles))}