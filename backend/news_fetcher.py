import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import json
import os
from config import settings
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse

class NewsFetcher:
    def __init__(self):
        self.feed_urls = settings.RSS_FEEDS
        self.raw_data_dir = "data/raw_news"
        self.processed_data_dir = "data/processed_news"
        self._ensure_directories()
        
        # Initialize NLTK components
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))

    def _ensure_directories(self):
        """Ensure required data directories exist"""
        for directory in [self.raw_data_dir, self.processed_data_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def generate_article_id(self, title: str, date: str) -> str:
        """Generate a unique ID for an article based on title and date"""
        content = f"{title}{date}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def _save_raw_article(self, article: Dict):
        """Save raw article data"""
        filename = f"{self.raw_data_dir}/{article['id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def _save_processed_article(self, article: Dict):
        """Save processed article data"""
        filename = f"{self.processed_data_dir}/{article['id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def _fetch_full_content(self, url: str) -> Optional[str]:
        """Attempt to fetch full article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()
            
            # Find main content (customize based on common article structures)
            content = None
            for selector in ['article', '.article-content', '.post-content', '.entry-content']:
                content = soup.select_one(selector)
                if content:
                    break
            
            if content:
                return content.get_text(separator=' ', strip=True)
            return None
            
        except Exception as e:
            print(f"Error fetching full content from {url}: {str(e)}")
            return None

    def _process_article(self, article: Dict) -> Dict:
        """Process article content and extract additional features"""
        processed_article = article.copy()
        
        # Attempt to fetch full content if summary is too short
        if len(article['content']) < 500:
            full_content = self._fetch_full_content(article['link'])
            if full_content:
                processed_article['full_content'] = full_content
        
        # Extract domain from source URL
        domain = urlparse(article['source']).netloc
        processed_article['domain'] = domain
        
        # Generate summary if full content is available
        if 'full_content' in processed_article:
            processed_article['summary'] = self._generate_summary(processed_article['full_content'])
        else:
            processed_article['summary'] = processed_article['content']
        
        # Extract named entities (if you have NER capabilities)
        # processed_article['entities'] = self._extract_entities(processed_article['content'])
        
        # Calculate reading time (assuming 200 words per minute)
        content = processed_article.get('full_content', processed_article['content'])
        word_count = len(content.split())
        processed_article['reading_time_minutes'] = max(1, round(word_count / 200))
        
        # Mark as processed
        processed_article['processed'] = True
        processed_article['processed_timestamp'] = datetime.utcnow().isoformat()
        
        return processed_article

    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a brief summary of the article content"""
        # Simple extractive summarization
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Score sentences based on position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            # Favor earlier sentences
            score += 1.0 / (i + 1)
            # Favor medium-length sentences
            words = len(sentence.split())
            if 10 <= words <= 30:
                score += 0.5
            
            scored_sentences.append((score, sentence))
        
        # Select top sentences while maintaining order
        top_sentences = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:max_sentences]
        summary_sentences = [s[1] for s in sorted(top_sentences, key=lambda x: sentences.index(x[1]))]
        
        return ' '.join(summary_sentences)

    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from all configured RSS feeds"""
        all_articles = []
        
        for feed_url in self.feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    article = {
                        "id": self.generate_article_id(entry.title, entry.get('published', '')),
                        "title": entry.title,
                        "content": entry.get('summary', ''),
                        "date": entry.get('published', ''),
                        "link": entry.get('link', ''),
                        "source": feed_url,
                        "categories": [tag.term for tag in entry.get('tags', [])],
                        "fetch_timestamp": datetime.utcnow().isoformat(),
                        "processed": False
                    }
                    
                    # Save raw article data
                    self._save_raw_article(article)
                    
                    # Process article
                    processed_article = self._process_article(article)
                    self._save_processed_article(processed_article)
                    
                    all_articles.append(processed_article)
                    
                    # Be nice to servers
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error fetching from {feed_url}: {str(e)}")
                continue
                
        return all_articles

    def get_stored_articles(self, processed: bool = True) -> List[Dict]:
        """Retrieve stored articles"""
        directory = self.processed_data_dir if processed else self.raw_data_dir
        articles = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                    articles.append(json.load(f))
                    
        return sorted(articles, key=lambda x: x['date'], reverse=True)

    def process_unprocessed_articles(self) -> int:
        """Process any unprocessed articles in the raw directory"""
        processed_count = 0
        raw_articles = self.get_stored_articles(processed=False)
        
        for article in raw_articles:
            if not article.get('processed', False):
                processed_article = self._process_article(article)
                self._save_processed_article(processed_article)
                processed_count += 1
                
                # Be nice to servers
                time.sleep(1)
        
        return processed_count
