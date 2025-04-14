from fastapi import FastAPI, HTTPException
from news_fetcher import NewsFetcher
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from llm_analyzer import LLMAnalyzer

app = FastAPI(title="DS Task AI News")
news_fetcher = NewsFetcher()
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
llm_analyzer = LLMAnalyzer()

@app.get("/")
async def root():
    return {"message": "Welcome to DS Task AI News API"}

@app.get("/fetch-news")
async def fetch_news():
    try:
        # Fetch articles
        articles = news_fetcher.fetch_articles()
        
        # Generate embeddings
        article_embeddings = embedding_generator.get_article_embeddings(articles)
        
        # Store in vector database
        vector_store.clear()  # Clear existing entries
        vector_store.add_articles(article_embeddings)
        
        return {"status": "success", "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar-articles/{article_id}")
async def get_similar_articles(article_id: str):
    try:
        # Fetch all articles to have the full context
        articles = news_fetcher.fetch_articles()
        articles_dict = {article['id']: article for article in articles}
        
        # Find the query article
        query_article = next((article for article in articles if article['id'] == article_id), None)
        if not query_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Generate embedding for the query article
        query_embedding = embedding_generator.get_article_embeddings([query_article])[article_id]
        
        # Find similar articles
        similar_article_ids = vector_store.search_similar(query_embedding, k=5)
        
        # Get the full article data for similar articles
        similar_articles = [articles_dict[aid] for aid in similar_article_ids if aid != article_id]
        
        return {"status": "success", "similar_articles": similar_articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze-article/{article_id}")
async def analyze_article(article_id: str):
    """Get detailed AI analysis of a specific article"""
    try:
        # Fetch all articles
        articles = news_fetcher.fetch_articles()
        
        # Find the target article
        article = next((article for article in articles if article['id'] == article_id), None)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get LLM analysis
        analysis = await llm_analyzer.analyze_article(article)
        
        return {
            "status": "success",
            "article": article,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topic-clusters")
async def get_topic_clusters():
    """Get AI-generated topic clusters from current news articles"""
    try:
        # Fetch articles
        articles = news_fetcher.fetch_articles()
        
        # Generate topic clusters
        clusters = await llm_analyzer.generate_topic_clusters(articles)
        
        return {
            "status": "success",
            "clusters": clusters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending-analysis")
async def get_trending_analysis():
    """Get analysis of trending topics and their significance"""
    try:
        # Fetch articles
        articles = news_fetcher.fetch_articles()
        
        # Prepare prompt for trending analysis
        prompt = f"""Analyze these news articles and identify:
        1. Top 3 trending topics
        2. Their significance and potential impact
        3. Related developments to watch

        Articles:
        {[article['title'] for article in articles[:10]]}  # Using top 10 articles
        """
        
        response = llm_analyzer.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a news analyst identifying trends and their significance."},
                {"role": "user", "content": prompt}
            ],
            model=llm_analyzer.model,
            temperature=0.3,
            max_tokens=1000
        )
        
        return {
            "status": "success",
            "trending_analysis": response.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
