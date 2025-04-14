from typing import List, Dict
from vector_store import VectorStore
from embeddings import EmbeddingGenerator

class Recommender:
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    def get_similar_articles(self, article_id: str, articles: List[Dict], k: int = 5) -> List[Dict]:
        """
        Find articles similar to the given article_id
        
        Args:
            article_id: ID of the article to find similar articles for
            articles: List of all articles to search through
            k: Number of similar articles to return
            
        Returns:
            List of similar articles
        """
        # Create a dictionary mapping article IDs to articles
        articles_dict = {article['id']: article for article in articles}
        
        # Find the query article
        query_article = articles_dict.get(article_id)
        if not query_article:
            return []
        
        # Generate embedding for the query article
        query_embedding = self.embedding_generator.get_article_embeddings([query_article])[article_id]
        
        # Find similar article IDs from the vector store
        similar_article_ids = self.vector_store.search_similar(query_embedding, k=k+1)  # +1 to account for the query article
        
        # Get the full article data for similar articles, excluding the query article
        similar_articles = [articles_dict[aid] for aid in similar_article_ids if aid != article_id]
        
        return similar_articles[:k]  # Limit to k results