from groq import Groq
from typing import List, Dict
from config import settings
import httpx

class LLMAnalyzer:
    def __init__(self):
        # Create a custom httpx client with the desired configuration
        http_client = httpx.Client(
            timeout=60.0,  # 60 seconds timeout
            follow_redirects=True
        )
        
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            http_client=http_client
        )
        # Using a llama model from Groq
        self.model = "llama-3.3-70b-versatile"
    
    async def analyze_article(self, article: Dict) -> Dict:
        """Analyze a single article and return key insights"""
        prompt = f"""Analyze this news article and provide key insights:

Title: {article['title']}
Content: {article['content']}

Please provide:
1. A brief summary (2-3 sentences)
2. Main topics/themes
3. Key takeaways
4. Sentiment (positive/negative/neutral)

Format the response as JSON."""

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a news analyst providing structured analysis of articles."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                "article_id": article['id'],
                "analysis": response.choices[0].message.content
            }
        except Exception as e:
            print(f"Error analyzing article: {str(e)}")
            raise

    async def generate_topic_clusters(self, articles: List[Dict]) -> Dict:
        """Group articles into topic clusters and provide summaries"""
        titles = "\n".join([f"- {article['title']}" for article in articles])
        
        prompt = f"""Given these news article titles:

{titles}

Group them into 3-5 main topic clusters. For each cluster:
1. Provide a cluster name/theme
2. List the relevant article titles
3. Write a brief overview of the cluster theme

Format the response as JSON."""

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a news analyst specializing in topic clustering and summarization."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                "clusters": response.choices[0].message.content
            }
        except Exception as e:
            print(f"Error generating topic clusters: {str(e)}")
            raise
