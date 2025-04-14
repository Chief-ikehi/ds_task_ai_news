import feedparser
from datetime import datetime
from typing import List, Dict, Optional, Set
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
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('news_fetcher')

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
            logger.warning(f"Error fetching full content from {url}: {str(e)}")
            return None

    def _process_article(self, article: Dict) -> Dict:
        """Process article content and extract additional features"""
        try:
            processed_article = article.copy()
            
            # Attempt to fetch full content if summary is too short
            if len(article.get('content', '')) < 500 and article.get('link'):
                full_content = self._fetch_full_content(article['link'])
                if full_content:
                    processed_article['full_content'] = full_content
            
            # Extract domain from source URL
            if 'source' in article and article['source']:
                domain = urlparse(article['source']).netloc
                processed_article['domain'] = domain
            else:
                processed_article['domain'] = "unknown"
            
            # Generate summary if full content is available
            if 'full_content' in processed_article:
                processed_article['summary'] = self._generate_summary(processed_article['full_content'])
            else:
                processed_article['summary'] = processed_article.get('content', '')
            
            # Calculate reading time (assuming 200 words per minute)
            content = processed_article.get('full_content', processed_article.get('content', ''))
            word_count = len(content.split())
            processed_article['reading_time_minutes'] = max(1, round(word_count / 200))
            
            # Mark as processed
            processed_article['processed'] = True
            processed_article['processed_timestamp'] = datetime.utcnow().isoformat()
            
            return processed_article
        except Exception as e:
            logger.error(f"Error processing article {article.get('id', 'unknown')}: {str(e)}")
            # Even if processing fails, mark it as processed to prevent retry loops
            article['processed'] = True
            article['processed_timestamp'] = datetime.utcnow().isoformat()
            article['processing_error'] = str(e)
            return article

    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a brief summary of the article content"""
        try:
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
        except Exception as e:
            logger.warning(f"Error generating summary: {str(e)}")
            # Return a portion of the text as a fallback
            if len(text) > 500:
                return text[:500] + "..."
            return text

    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from all configured RSS feeds"""
        all_articles = []
        
        for feed_url in self.feed_urls:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    try:
                        article_id = self.generate_article_id(entry.title, entry.get('published', ''))
                        
                        article = {
                            "id": article_id,
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
                        logger.error(f"Error processing entry {entry.get('title', 'unknown')}: {str(e)}")
                        continue
                    
            except Exception as e:
                logger.error(f"Error fetching from {feed_url}: {str(e)}")
                continue
                
        # Process any unprocessed articles to ensure no missing articles
        self.process_missing_articles()
        
        return all_articles

    def get_stored_articles(self, processed: bool = True) -> List[Dict]:
        """Retrieve stored articles"""
        directory = self.processed_data_dir if processed else self.raw_data_dir
        articles = []
        
        try:
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                            articles.append(json.load(f))
                    except Exception as e:
                        logger.error(f"Error reading article file {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading directory {directory}: {str(e)}")
                    
        return sorted(articles, key=lambda x: x.get('date', ''), reverse=True)

    def get_raw_article_ids(self) -> Set[str]:
        """Get the set of all raw article IDs from filenames"""
        raw_ids = set()
        try:
            for filename in os.listdir(self.raw_data_dir):
                if filename.endswith('.json'):
                    # Extract ID from filename (removing .json extension)
                    article_id = filename[:-5]
                    raw_ids.add(article_id)
        except Exception as e:
            logger.error(f"Error getting raw article IDs: {str(e)}")
        return raw_ids
    
    def get_processed_article_ids(self) -> Set[str]:
        """Get the set of all processed article IDs from filenames"""
        processed_ids = set()
        try:
            for filename in os.listdir(self.processed_data_dir):
                if filename.endswith('.json'):
                    # Extract ID from filename (removing .json extension)
                    article_id = filename[:-5]
                    processed_ids.add(article_id)
        except Exception as e:
            logger.error(f"Error getting processed article IDs: {str(e)}")
        return processed_ids

    def process_unprocessed_articles(self) -> int:
        """Process any articles in the raw directory marked as unprocessed"""
        processed_count = 0
        raw_articles = self.get_stored_articles(processed=False)
        
        for article in raw_articles:
            try:
                if not article.get('processed', False):
                    logger.info(f"Processing previously unprocessed article: {article.get('id', 'unknown')}")
                    processed_article = self._process_article(article)
                    self._save_processed_article(processed_article)
                    processed_count += 1
                    
                    # Be nice to servers
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error during processing article {article.get('id', 'unknown')}: {str(e)}")
                # Even if processing fails, save what we can to prevent endless retries
                article['processing_error'] = str(e)
                article['processed'] = True
                article['processed_timestamp'] = datetime.utcnow().isoformat()
                self._save_processed_article(article)
        
        return processed_count
        
    def process_missing_articles(self) -> int:
        """
        Process any articles that exist in raw directory but not in processed directory
        This is a more thorough approach than just checking the 'processed' flag
        """
        raw_ids = self.get_raw_article_ids()
        processed_ids = self.get_processed_article_ids()
        
        # Find IDs that are in raw but not in processed
        missing_ids = raw_ids - processed_ids
        processed_count = 0
        
        logger.info(f"Found {len(missing_ids)} articles missing from processed directory")
        
        for article_id in missing_ids:
            try:
                # Load the raw article
                with open(f"{self.raw_data_dir}/{article_id}.json", 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                logger.info(f"Processing missing article: {article_id}")
                processed_article = self._process_article(article)
                self._save_processed_article(processed_article)
                processed_count += 1
                
                # Be nice to servers
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing missing article {article_id}: {str(e)}")
                # Create a minimal processed version to prevent endless retries
                try:
                    with open(f"{self.raw_data_dir}/{article_id}.json", 'r', encoding='utf-8') as f:
                        article = json.load(f)
                    
                    article['processed'] = True
                    article['processed_timestamp'] = datetime.utcnow().isoformat()
                    article['processing_error'] = str(e)
                    self._save_processed_article(article)
                except Exception as inner_e:
                    logger.error(f"Failed to create minimal processed article for {article_id}: {str(inner_e)}")
        
        return processed_count
    
    def sync_raw_processed(self):
        """
        Synchronize raw and processed articles to ensure all raw articles have processed versions
        Returns a tuple of (processed_count, error_count)
        """
        processed_count = self.process_missing_articles()
        unprocessed_count = self.process_unprocessed_articles()
        
        total_processed = processed_count + unprocessed_count
        logger.info(f"Synchronized raw and processed articles. Processed {total_processed} articles.")
        
        # Count articles with processing errors
        error_count = 0
        processed_articles = self.get_stored_articles(processed=True)
        for article in processed_articles:
            if 'processing_error' in article:
                error_count += 1
        
        logger.info(f"Articles with processing errors: {error_count}")
        
        return (total_processed, error_count)