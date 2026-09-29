"""
Secure YouTube search module for JARVIS
Provides YouTube search functionality with URL validation and cross-platform browser support.
"""

import webbrowser
import urllib.parse
import logging
import platform
from typing import Optional
from .helpers import speak, validate_url, sanitize_input

logger = logging.getLogger(__name__)

class YouTubeService:
    """Secure YouTube service for searching and opening videos."""
    
    def __init__(self):
        """Initialize YouTube service with platform-specific browser configuration."""
        self.base_search_url = "https://www.youtube.com/results?search_query="
        self.base_video_url = "https://www.youtube.com/watch?v="
        self.platform = platform.system().lower()
        
        logger.info(f"YouTube service initialized for {self.platform} platform")
    
    def search(self, query: str) -> bool:
        """
        Search for videos on YouTube.
        
        Args:
            query: Search query string
        
        Returns:
            True if search was successful, False otherwise
        """
        try:
            if not query or not query.strip():
                speak("Please provide a search term.")
                return False
            
            # Sanitize the search query
            sanitized_query = sanitize_input(query.strip())
            
            if not sanitized_query:
                speak("Sorry, the search term appears to be invalid.")
                return False
            
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(sanitized_query)
            search_url = f"{self.base_search_url}{encoded_query}"
            
            # Validate the URL before opening
            if not validate_url(search_url):
                logger.error(f"Invalid search URL generated: {search_url}")
                speak("Sorry, I couldn't create a valid search URL.")
                return False
            
            # Open the search in browser
            webbrowser.open(search_url)
            speak(f"Opening YouTube search results for {sanitized_query}")
            
            logger.info(f"YouTube search performed: {sanitized_query}")
            return True
            
        except Exception as e:
            logger.error(f"Error performing YouTube search: {e}")
            speak("Sorry, I couldn't perform the YouTube search.")
            return False
    
    def open_video_by_id(self, video_id: str) -> bool:
        """
        Open a specific YouTube video by its ID.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not video_id or not video_id.strip():
                speak("Please provide a valid video ID.")
                return False
            
            # Basic validation for YouTube video ID format
            sanitized_id = sanitize_input(video_id.strip())
            
            # YouTube video IDs are typically 11 characters long and contain alphanumeric characters, hyphens, and underscores
            if len(sanitized_id) != 11 or not all(c.isalnum() or c in '-_' for c in sanitized_id):
                speak("The provided video ID doesn't appear to be valid.")
                return False
            
            video_url = f"{self.base_video_url}{sanitized_id}"
            
            if not validate_url(video_url):
                logger.error(f"Invalid video URL: {video_url}")
                speak("Sorry, I couldn't create a valid video URL.")
                return False
            
            webbrowser.open(video_url)
            speak("Opening YouTube video")
            
            logger.info(f"YouTube video opened: {sanitized_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error opening YouTube video: {e}")
            speak("Sorry, I couldn't open the YouTube video.")
            return False
    
    def open_channel(self, channel_name: str) -> bool:
        """
        Open a YouTube channel by name.
        
        Args:
            channel_name: Channel name or handle
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not channel_name or not channel_name.strip():
                speak("Please provide a channel name.")
                return False
            
            sanitized_name = sanitize_input(channel_name.strip())
            
            if not sanitized_name:
                speak("The channel name appears to be invalid.")
                return False
            
            # Create channel search URL
            encoded_name = urllib.parse.quote_plus(f"{sanitized_name} channel")
            channel_url = f"{self.base_search_url}{encoded_name}&sp=EgIQAg%253D%253D"  # Filter for channels
            
            if not validate_url(channel_url):
                logger.error(f"Invalid channel URL: {channel_url}")
                speak("Sorry, I couldn't create a valid channel URL.")
                return False
            
            webbrowser.open(channel_url)
            speak(f"Searching for {sanitized_name} channel on YouTube")
            
            logger.info(f"YouTube channel search: {sanitized_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error opening YouTube channel: {e}")
            speak("Sorry, I couldn't search for that channel.")
            return False

# Global YouTube service instance
_youtube_service = YouTubeService()

def youtube_search(query: str) -> bool:
    """
    Search YouTube for the given query.
    
    Args:
        query: Search query string
    
    Returns:
        True if successful, False otherwise
    """
    return _youtube_service.search(query)

def open_youtube_video(video_id: str) -> bool:
    """
    Open a specific YouTube video.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        True if successful, False otherwise
    """
    return _youtube_service.open_video_by_id(video_id)

def open_youtube_channel(channel_name: str) -> bool:
    """
    Open/search for a YouTube channel.
    
    Args:
        channel_name: Channel name
    
    Returns:
        True if successful, False otherwise
    """
    return _youtube_service.open_channel(channel_name)

def open_youtube_home() -> bool:
    """
    Open YouTube homepage.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        youtube_url = "https://www.youtube.com"
        
        if not validate_url(youtube_url):
            logger.error("YouTube homepage URL validation failed")
            return False
        
        webbrowser.open(youtube_url)
        speak("Opening YouTube")
        
        logger.info("YouTube homepage opened")
        return True
        
    except Exception as e:
        logger.error(f"Error opening YouTube homepage: {e}")
        speak("Sorry, I couldn't open YouTube.")
        return False