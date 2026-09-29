"""
Dictionary and word lookup module for JARVIS
Provides word definitions, synonyms, and pronunciation using various APIs and local resources.
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
from difflib import get_close_matches
from .helpers import speak, sanitize_input, create_data_directory

logger = logging.getLogger(__name__)

class DictionaryService:
    """
    Dictionary service with multiple data sources for word definitions and meanings.
    """
    
    def __init__(self):
        """Initialize the dictionary service."""
        self.data_dir = create_data_directory()
        self.cache_file = self.data_dir / 'word_cache.json'
        self.word_cache = self._load_cache()
        
        # Free dictionary APIs (no key required)
        self.apis = {
            'free_dictionary': 'https://api.dictionaryapi.dev/api/v2/entries/en/',
            'wordnik': 'https://api.wordnik.com/v4/word.json/',  # Requires API key
        }
        
        logger.info("Dictionary service initialized")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached word definitions."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading word cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save word definitions to cache."""
        try:
            # Keep only the most recent 1000 entries
            if len(self.word_cache) > 1000:
                # Keep the most recent entries (assuming they're more likely to be accessed again)
                items = list(self.word_cache.items())
                self.word_cache = dict(items[-1000:])
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.word_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving word cache: {e}")
    
    def _fetch_definition_from_api(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Fetch word definition from online API.
        
        Args:
            word: Word to look up
        
        Returns:
            Dictionary with word information or None if failed
        """
        try:
            # Try free dictionary API first
            url = f"{self.apis['free_dictionary']}{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    word_data = data[0]
                    
                    # Extract relevant information
                    result = {
                        'word': word_data.get('word', word),
                        'phonetic': word_data.get('phonetic', ''),
                        'meanings': []
                    }
                    
                    for meaning in word_data.get('meanings', []):
                        part_of_speech = meaning.get('partOfSpeech', 'unknown')
                        definitions = []
                        
                        for definition in meaning.get('definitions', []):
                            def_text = definition.get('definition', '')
                            example = definition.get('example', '')
                            definitions.append({
                                'definition': def_text,
                                'example': example
                            })
                        
                        if definitions:
                            result['meanings'].append({
                                'partOfSpeech': part_of_speech,
                                'definitions': definitions
                            })
                    
                    return result
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error fetching definition from API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing API response: {e}")
            return None
    
    def _format_definition_for_speech(self, word_data: Dict[str, Any]) -> str:
        """
        Format word definition for text-to-speech.
        
        Args:
            word_data: Word data dictionary
        
        Returns:
            Formatted string for speech
        """
        try:
            word = word_data.get('word', 'Unknown')
            phonetic = word_data.get('phonetic', '')
            meanings = word_data.get('meanings', [])
            
            # Start with word and pronunciation
            speech_text = f"The word {word}"
            if phonetic:
                speech_text += f", pronounced {phonetic},"
            
            # Add meanings
            if not meanings:
                speech_text += " could not be found in the dictionary."
                return speech_text
            
            speech_text += " means: "
            
            for i, meaning in enumerate(meanings[:2]):  # Limit to first 2 meanings
                part_of_speech = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                if definitions:
                    definition = definitions[0].get('definition', '')
                    if part_of_speech:
                        speech_text += f"As a {part_of_speech}, {definition}. "
                    else:
                        speech_text += f"{definition}. "
                    
                    # Add example if available
                    example = definitions[0].get('example', '')
                    if example:
                        speech_text += f"For example: {example}. "
            
            return speech_text
            
        except Exception as e:
            logger.error(f"Error formatting definition for speech: {e}")
            return f"Sorry, I couldn't format the definition for {word_data.get('word', 'the word')}."
    
    def lookup_word(self, word: str) -> bool:
        """
        Look up a word definition and speak it.
        
        Args:
            word: Word to look up
        
        Returns:
            True if definition found and spoken, False otherwise
        """
        try:
            if not word or not word.strip():
                speak("Please provide a word to look up.")
                return False
            
            # Sanitize and normalize the word
            clean_word = sanitize_input(word.strip().lower())
            
            if not clean_word or len(clean_word) > 50:
                speak("Invalid word provided.")
                return False
            
            # Check cache first
            if clean_word in self.word_cache:
                word_data = self.word_cache[clean_word]
                definition_text = self._format_definition_for_speech(word_data)
                speak(definition_text)
                logger.info(f"Word definition retrieved from cache: {clean_word}")
                return True
            
            # Fetch from API
            speak(f"Looking up the word {clean_word}...")
            word_data = self._fetch_definition_from_api(clean_word)
            
            if word_data:
                # Cache the result
                self.word_cache[clean_word] = word_data
                self._save_cache()
                
                # Speak the definition
                definition_text = self._format_definition_for_speech(word_data)
                speak(definition_text)
                
                logger.info(f"Word definition found and spoken: {clean_word}")
                return True
            else:
                # Try to find similar words
                similar_words = self._find_similar_words(clean_word)
                if similar_words:
                    similar = ', '.join(similar_words[:3])
                    speak(f"I couldn't find the definition for {clean_word}. Did you mean: {similar}?")
                else:
                    speak(f"Sorry, I couldn't find the definition for {clean_word}.")
                
                return False
                
        except Exception as e:
            logger.error(f"Error looking up word: {e}")
            speak("Sorry, I encountered an error while looking up the word.")
            return False
    
    def _find_similar_words(self, word: str) -> List[str]:
        """
        Find similar words in cache for suggestions.
        
        Args:
            word: Word to find similarities for
        
        Returns:
            List of similar words
        """
        try:
            cached_words = list(self.word_cache.keys())
            if not cached_words:
                return []
            
            similar = get_close_matches(word, cached_words, n=3, cutoff=0.6)
            return similar
            
        except Exception as e:
            logger.error(f"Error finding similar words: {e}")
            return []
    
    def spell_word(self, word: str) -> bool:
        """
        Spell out a word letter by letter.
        
        Args:
            word: Word to spell
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not word or not word.strip():
                speak("Please provide a word to spell.")
                return False
            
            clean_word = sanitize_input(word.strip())
            
            if not clean_word.isalpha():
                speak("I can only spell words with letters.")
                return False
            
            if len(clean_word) > 20:
                speak("That word is too long to spell out.")
                return False
            
            # Spell the word
            letters = ' - '.join(clean_word.upper())
            speak(f"The word {clean_word} is spelled: {letters}")
            
            logger.info(f"Word spelled: {clean_word}")
            return True
            
        except Exception as e:
            logger.error(f"Error spelling word: {e}")
            speak("Sorry, I couldn't spell that word.")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the word cache.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = {
                'total_words': len(self.word_cache),
                'cache_size_bytes': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
                'cache_location': str(self.cache_file)
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """
        Clear the word definition cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.word_cache = {}
            if self.cache_file.exists():
                self.cache_file.unlink()
            
            speak("Dictionary cache cleared.")
            logger.info("Dictionary cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            speak("Error clearing dictionary cache.")
            return False

# Global dictionary service
_dictionary_service = DictionaryService()

def lookup_word(word: str) -> bool:
    """
    Look up a word definition.
    
    Args:
        word: Word to look up
    
    Returns:
        True if successful, False otherwise
    """
    return _dictionary_service.lookup_word(word)

def spell_word(word: str) -> bool:
    """
    Spell out a word.
    
    Args:
        word: Word to spell
    
    Returns:
        True if successful, False otherwise
    """
    return _dictionary_service.spell_word(word)

def get_dictionary_stats() -> Dict[str, Any]:
    """
    Get dictionary service statistics.
    
    Returns:
        Dictionary statistics
    """
    return _dictionary_service.get_cache_stats()

def clear_dictionary_cache() -> bool:
    """
    Clear the dictionary cache.
    
    Returns:
        True if successful, False otherwise
    """
    return _dictionary_service.clear_cache()