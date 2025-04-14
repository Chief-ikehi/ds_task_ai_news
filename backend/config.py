from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    COHERE_API_KEY: str
    GROQ_API_KEY: str
    
    # RSS Feed URLs
    RSS_FEEDS: List[str] = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml"
    ]
    
    # Vector DB Settings
    VECTOR_DB_TYPE: str = "faiss"  # can be "pinecone", "weaviate", or "faiss"
    VECTOR_DIMENSION: int = 1024  # Cohere embedding dimension
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
