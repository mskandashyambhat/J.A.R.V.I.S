"""
Secure web browser module for JARVIS
Provides safe web browsing functionality with URL validation and cross-platform support.
"""

import webbrowser
import urllib.parse
import logging
import platform
import re
from typing import Optional, Dict, Any
from .helpers import speak, validate_url, sanitize_input

logger = logging.getLogger(__name__)

class SecureWebBrowser:
    """Secure web browser service with URL validation and safety checks."""
    
    def __init__(self):
        """Initialize the secure web browser service."""
        self.platform = platform.system().lower()
        
        # Common safe websites that users might want to access
        self.safe_sites = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'github': 'https://www.github.com',
            'wikipedia': 'https://www.wikipedia.org',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://www.reddit.com',
            'news': 'https://news.google.com',
            'weather': 'https://weather.com',
            'maps': 'https://maps.google.com',
            'gmail': 'https://mail.google.com',
            'drive': 'https://drive.google.com',
            'docs': 'https://docs.google.com',
            'amazon': 'https://www.amazon.com',
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://www.spotify.com'
        }
        
        logger.info(f"Secure web browser initialized for {self.platform} platform")
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL by adding protocol if missing.
        
        Args:
            url: Raw URL string
        
        Returns:
            Normalized URL with protocol
        """
        url = url.strip().lower()
        
        if not url.startswith(('http://', 'https://')):
            # Add https by default for security
            url = 'https://' + url
        
        return url
    
    def _is_safe_domain(self, url: str) -> bool:
        """
        Check if a domain is in the safe list or appears legitimate.
        
        Args:
            url: URL to check
        
        Returns:
            True if domain appears safe, False otherwise
        """
        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for comparison
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check against known safe sites
            for safe_domain in self.safe_sites.values():
                safe_parsed = urlparse(safe_domain)
                safe_domain_clean = safe_parsed.netloc.lower()
                if safe_domain_clean.startswith('www.'):
                    safe_domain_clean = safe_domain_clean[4:]
                
                if domain == safe_domain_clean:
                    return True
            
            # Basic checks for legitimate domains
            # Must have at least one dot and valid characters
            if '.' not in domain:
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'localhost',
                r'127\.0\.0\.1',
                r'0\.0\.0\.0',
                r'192\.168\.',
                r'10\.',
                r'172\.(1[6-9]|2[0-9]|3[0-1])\.',
                r'[^a-zA-Z0-9.-]',  # Invalid characters
                r'\.\.+',  # Multiple consecutive dots
                r'^[0-9]+$'  # All numeric
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, domain):
                    return False
            
            # Must end with valid TLD
            tld = domain.split('.')[-1]
            common_tlds = ['com', 'org', 'net', 'edu', 'gov', 'mil', 'int', 'co', 'io', 'ly', 'me', 'tv']
            country_tlds = ['uk', 'ca', 'au', 'de', 'fr', 'jp', 'in', 'br', 'mx', 'it', 'es', 'ru', 'cn']
            
            if tld not in common_tlds and tld not in country_tlds:
                logger.warning(f"Uncommon TLD detected: {tld}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking domain safety: {e}")
            return False
    
    def open_url(self, url: str, confirm_unsafe: bool = True) -> bool:
        """
        Safely open a URL in the default browser.
        
        Args:
            url: URL to open
            confirm_unsafe: Whether to ask for confirmation for potentially unsafe URLs
        
        Returns:
            True if URL was opened successfully, False otherwise
        """
        try:
            if not url or not url.strip():
                speak("Please provide a valid URL.")
                return False
            
            # Sanitize and normalize the URL
            sanitized_url = sanitize_input(url.strip())
            normalized_url = self._normalize_url(sanitized_url)
            
            # Validate URL format
            if not validate_url(normalized_url):
                speak("The provided URL doesn't appear to be valid.")
                logger.warning(f"Invalid URL rejected: {url}")
                return False
            
            # Check if domain is safe
            if not self._is_safe_domain(normalized_url):
                if confirm_unsafe:
                    speak("This website may not be safe. Opening anyway, but please be careful.")
                    logger.warning(f"Potentially unsafe URL opened: {normalized_url}")
                else:
                    speak("Sorry, I cannot open that website for security reasons.")
                    logger.warning(f"Unsafe URL blocked: {normalized_url}")
                    return False
            
            # Open the URL
            webbrowser.open(normalized_url)
            speak(f"Opening website: {normalized_url}")
            
            logger.info(f"Website opened successfully: {normalized_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            speak("Sorry, I couldn't open that website.")
            return False
    
    def open_safe_site(self, site_name: str) -> bool:
        """
        Open a pre-approved safe website by name.
        
        Args:
            site_name: Name of the safe site
        
        Returns:
            True if successful, False otherwise
        """
        try:
            site_name = site_name.lower().strip()
            
            if site_name in self.safe_sites:
                url = self.safe_sites[site_name]
                webbrowser.open(url)
                speak(f"Opening {site_name}")
                logger.info(f"Safe site opened: {site_name} -> {url}")
                return True
            else:
                available_sites = ', '.join(self.safe_sites.keys())
                speak(f"I don't have {site_name} in my safe sites list. Available sites are: {available_sites}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening safe site: {e}")
            speak("Sorry, I couldn't open that website.")
            return False
    
    def search_web(self, query: str, search_engine: str = 'google') -> bool:
        """
        Perform a web search using the specified search engine.
        
        Args:
            query: Search query
            search_engine: Search engine to use ('google', 'bing', 'duckduckgo')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not query or not query.strip():
                speak("Please provide a search term.")
                return False
            
            sanitized_query = sanitize_input(query.strip())
            
            if not sanitized_query:
                speak("The search term appears to be invalid.")
                return False
            
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(sanitized_query)
            
            # Select search engine
            search_engines = {
                'google': f'https://www.google.com/search?q={encoded_query}',
                'bing': f'https://www.bing.com/search?q={encoded_query}',
                'duckduckgo': f'https://duckduckgo.com/?q={encoded_query}'
            }
            
            search_engine = search_engine.lower()
            if search_engine not in search_engines:
                search_engine = 'google'  # Default fallback
            
            search_url = search_engines[search_engine]
            
            if not validate_url(search_url):
                logger.error(f"Invalid search URL: {search_url}")
                speak("Sorry, I couldn't create a valid search URL.")
                return False
            
            webbrowser.open(search_url)
            speak(f"Searching for {sanitized_query} on {search_engine}")
            
            logger.info(f"Web search performed: {sanitized_query} on {search_engine}")
            return True
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            speak("Sorry, I couldn't perform the web search.")
            return False
    
    def get_safe_sites_list(self) -> Dict[str, str]:
        """
        Get the list of pre-approved safe websites.
        
        Returns:
            Dictionary of safe sites
        """
        return self.safe_sites.copy()

# Global web browser service instance
_web_browser = SecureWebBrowser()

def open_website(url: str) -> bool:
    """
    Open a website safely.
    
    Args:
        url: Website URL
    
    Returns:
        True if successful, False otherwise
    """
    return _web_browser.open_url(url)

def open_safe_website(site_name: str) -> bool:
    """
    Open a pre-approved safe website.
    
    Args:
        site_name: Name of the safe site
    
    Returns:
        True if successful, False otherwise
    """
    return _web_browser.open_safe_site(site_name)

def search_web(query: str, engine: str = 'google') -> bool:
    """
    Search the web using the specified search engine.
    
    Args:
        query: Search query
        engine: Search engine ('google', 'bing', 'duckduckgo')
    
    Returns:
        True if successful, False otherwise
    """
    return _web_browser.search_web(query, engine)

def get_available_safe_sites() -> Dict[str, str]:
    """
    Get the list of available safe websites.
    
    Returns:
        Dictionary of safe sites
    """
    return _web_browser.get_safe_sites_list()