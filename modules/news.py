"""
Secure news module for JARVIS
Fetches news headlines using NewsAPI with proper API key management and error handling.
"""

import requests
import json
import os
import logging
from typing import Optional, List, Dict, Any
from .helpers import speak

logger = logging.getLogger(__name__)

class NewsService:
    """Secure news service that respects privacy and uses environment variables for API keys."""
    
    def __init__(self):
        """Initialize the news service with API configuration."""
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        self.default_country = "us"  # Can be configured
        self.default_category = "general"
        self.max_headlines = 5  # Limit to avoid overwhelming the user
        
        if not self.api_key:
            logger.warning("No NEWS_API_KEY found in environment variables. News feature disabled.")
    
    def is_available(self) -> bool:
        """Check if the news service is available (has API key)."""
        return bool(self.api_key)
    
    def get_top_headlines(self, country: str = None, category: str = None, max_results: int = None) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch top news headlines.
        
        Args:
            country: Country code (e.g., 'us', 'gb', 'in')
            category: News category (business, entertainment, general, health, science, sports, technology)
            max_results: Maximum number of headlines to return
        
        Returns:
            List of news articles or None if failed
        """
        if not self.is_available():
            logger.error("News service not available - no API key")
            return None
        
        try:
            country = country or self.default_country
            category = category or self.default_category
            max_results = max_results or self.max_headlines
            
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'category': category,
                'pageSize': min(max_results, 20)  # API limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"Retrieved {len(articles)} news headlines")
                return articles[:max_results]
            else:
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching news: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing news JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {e}")
            return None
    
    def search_news(self, query: str, max_results: int = None) -> Optional[List[Dict[str, Any]]]:
        """
        Search for news articles by query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            List of news articles or None if failed
        """
        if not self.is_available():
            logger.error("News service not available - no API key")
            return None
        
        try:
            max_results = max_results or self.max_headlines
            
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'q': query,
                'sortBy': 'publishedAt',
                'pageSize': min(max_results, 20),
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                logger.info(f"Found {len(articles)} articles for query: {query}")
                return articles[:max_results]
            else:
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error searching news: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing news JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching news: {e}")
            return None
    
    def format_article_for_speech(self, article: Dict[str, Any]) -> str:
        """
        Format a news article for text-to-speech.
        
        Args:
            article: News article dictionary
        
        Returns:
            Formatted string for speech
        """
        try:
            title = article.get('title', 'No title available')
            source = article.get('source', {}).get('name', 'Unknown source')
            
            # Clean up title (remove source name if it's at the end)
            if title.endswith(f" - {source}"):
                title = title[:-len(f" - {source}")]
            
            return f"From {source}: {title}"
            
        except Exception as e:
            logger.error(f"Error formatting article: {e}")
            return "Error reading article"

# Global news service instance
_news_service = NewsService()

def speak_news(category: str = None, country: str = None) -> bool:
    """
    Speak the latest news headlines.
    
    Args:
        category: News category filter
        country: Country code filter
    
    Returns:
        True if news was spoken successfully, False otherwise
    """
    try:
        if not _news_service.is_available():
            speak("Sorry, the news service is not available. Please set up your NewsAPI key.")
            return False
        
        speak("Getting the latest news headlines...")
        
        articles = _news_service.get_top_headlines(country=country, category=category)
        
        if not articles:
            speak("Sorry, I couldn't fetch the news right now. Please try again later.")
            return False
        
        if len(articles) == 0:
            speak("No news articles found.")
            return False
        
        speak(f"Here are the top {len(articles)} news headlines:")
        
        for i, article in enumerate(articles, 1):
            headline = _news_service.format_article_for_speech(article)
            speak(f"Headline {i}: {headline}")
            
            # Add a small pause between headlines
            if i < len(articles):
                speak("Next headline.")
        
        speak("Those were the latest news headlines.")
        logger.info(f"Successfully spoke {len(articles)} news headlines")
        return True
        
    except Exception as e:
        logger.error(f"Error speaking news: {e}")
        speak("Sorry, I encountered an error while getting the news.")
        return False

def search_specific_news(query: str) -> bool:
    """
    Search and speak news about a specific topic.
    
    Args:
        query: Search query
    
    Returns:
        True if news was found and spoken, False otherwise
    """
    try:
        if not _news_service.is_available():
            speak("Sorry, the news service is not available. Please set up your NewsAPI key.")
            return False
        
        speak(f"Searching for news about {query}...")
        
        articles = _news_service.search_news(query)
        
        if not articles or len(articles) == 0:
            speak(f"Sorry, I couldn't find any recent news about {query}.")
            return False
        
        speak(f"Here are the latest articles about {query}:")
        
        for i, article in enumerate(articles, 1):
            headline = _news_service.format_article_for_speech(article)
            speak(f"Article {i}: {headline}")
            
            if i < len(articles):
                speak("Next article.")
        
        logger.info(f"Successfully found and spoke {len(articles)} articles about {query}")
        return True
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        speak("Sorry, I encountered an error while searching for news.")
        return False

def get_news_url() -> Optional[str]:
    """
    Get a URL for reading more news details.
    
    Returns:
        URL string or None if not available
    """
    try:
        if not _news_service.is_available():
            return None
        
        articles = _news_service.get_top_headlines(max_results=1)
        
        if articles and len(articles) > 0:
            url = articles[0].get('url')
            if url:
                logger.info(f"Providing news URL: {url}")
                return url
        
        # Fallback to general news website
        return "https://news.google.com"
        
    except Exception as e:
        logger.error(f"Error getting news URL: {e}")
        return "https://news.google.com"

def get_news_by_category(category: str) -> bool:
    """
    Get news by specific category.
    
    Args:
        category: News category (business, entertainment, general, health, science, sports, technology)
    
    Returns:
        True if successful, False otherwise
    """
    valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
    
    if category.lower() not in valid_categories:
        speak(f"Sorry, {category} is not a valid news category. Available categories are: {', '.join(valid_categories)}")
        return False
    
    return speak_news(category=category.lower())

def get_local_news(country_code: str = "us") -> bool:
    """
    Get news for a specific country.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
    
    Returns:
        True if successful, False otherwise
    """
    return speak_news(country=country_code.lower())

def check_news_service_status() -> Dict[str, Any]:
    """
    Check the status of the news service.
    
    Returns:
        Dictionary with service status information
    """
    status = {
        'available': _news_service.is_available(),
        'api_key_set': bool(_news_service.api_key),
        'base_url': _news_service.base_url
    }
    
    if status['available']:
        try:
            # Test the service with a simple request
            test_articles = _news_service.get_top_headlines(max_results=1)
            status['working'] = test_articles is not None
        except Exception as e:
            status['working'] = False
            status['error'] = str(e)
    else:
        status['working'] = False
    
    return status