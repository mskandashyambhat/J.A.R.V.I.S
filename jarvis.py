#!/usr/bin/env python3
"""
JARVIS - Just A Rather Very Intelligent System
A secure, privacy-focused voice assistant that keeps your data local.

Created as a secure replica with the following improvements:
- No hardcoded credentials
- Environment variable configuration
- Local data storage only
- Cross-platform compatibility
- Enhanced security measures
"""

import pyttsx3
import wikipedia
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import platform
from pathlib import Path
import logging
from typing import Optional

# Import local modules
from modules.helpers import speak, take_command, get_weather, screenshot, get_cpu_info, tell_joke
from modules.news import speak_news, get_news_url
from modules.youtube_search import youtube_search
from modules.email_handler import send_email
from modules.face_recognition import authenticate_user
from modules.dictionary import lookup_word

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JARVIS:
    """Main JARVIS class with secure, cross-platform functionality."""
    
    def __init__(self):
        """Initialize JARVIS with secure defaults."""
        self.platform = platform.system().lower()
        self.data_dir = Path.home() / '.jarvis'
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        # Set up browser paths based on platform
        self._setup_browser()
        
        logger.info(f"JARVIS initialized on {self.platform} platform")
    
    def _setup_browser(self):
        """Set up browser configuration based on the current platform."""
        try:
            if self.platform == 'darwin':  # macOS
                self.chrome_path = 'open -a "Google Chrome" %s'
            elif self.platform == 'linux':
                self.chrome_path = '/usr/bin/google-chrome %s'
            elif self.platform == 'windows':
                self.chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe %s'
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                self.chrome_path = None
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            self.chrome_path = None
    
    def wish_user(self):
        """Greet the user based on time of day and provide weather info."""
        hour = datetime.datetime.now().hour
        
        if 0 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"
        
        speak(f"{greeting} I am JARVIS, your personal assistant.")
        
        # Get weather info if available
        weather_info = get_weather()
        if weather_info:
            speak(weather_info)
        
        speak("How can I help you today?")
    
    def open_website(self, url: str):
        """Safely open a website in the default browser."""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
        except Exception as e:
            logger.error(f"Error opening website {url}: {e}")
            speak("Sorry, I couldn't open that website.")
    
    def search_web(self, query: str):
        """Perform a web search using the default browser."""
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.open_website(search_url)
            speak(f"Here's what I found for {query}")
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            speak("Sorry, I couldn't perform the search.")
    
    def search_maps(self, location: str):
        """Search for a location on Google Maps."""
        try:
            maps_url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
            self.open_website(maps_url)
            speak(f"Here is the location for {location}")
        except Exception as e:
            logger.error(f"Error searching maps: {e}")
            speak("Sorry, I couldn't find that location.")
    
    def remember_note(self, note: str):
        """Save a note to local storage."""
        try:
            notes_file = self.data_dir / 'notes.txt'
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(notes_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {note}\n")
            
            speak(f"I've remembered that: {note}")
            logger.info(f"Note saved: {note}")
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            speak("Sorry, I couldn't save that note.")
    
    def recall_notes(self):
        """Read back saved notes."""
        try:
            notes_file = self.data_dir / 'notes.txt'
            
            if not notes_file.exists():
                speak("You haven't asked me to remember anything yet.")
                return
            
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = f.read().strip()
            
            if notes:
                speak("Here are your notes:")
                speak(notes.replace('\n', '. '))
            else:
                speak("You haven't asked me to remember anything yet.")
                
        except Exception as e:
            logger.error(f"Error reading notes: {e}")
            speak("Sorry, I couldn't access your notes.")
    
    def execute_command(self, query: str):
        """Execute user commands safely and securely."""
        query = query.lower().strip()
        logger.info(f"Processing command: {query}")
        
        try:
            # Wikipedia searches
            if 'wikipedia' in query:
                speak('Searching Wikipedia...')
                search_term = query.replace('wikipedia', '').strip()
                if search_term:
                    try:
                        results = wikipedia.summary(search_term, sentences=2)
                        speak('According to Wikipedia:')
                        speak(results)
                    except wikipedia.exceptions.DisambiguationError as e:
                        speak(f"Multiple results found. Please be more specific. Options include: {', '.join(e.options[:3])}")
                    except wikipedia.exceptions.PageError:
                        speak("Sorry, I couldn't find information about that topic.")
                else:
                    speak("What would you like me to search on Wikipedia?")
            
            # Voice switching
            elif 'change voice' in query or 'switch voice' in query:
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    current_voice = self.engine.getProperty('voice')
                    new_voice = voices[1].id if current_voice == voices[0].id else voices[0].id
                    self.engine.setProperty('voice', new_voice)
                    speak("I've changed my voice. How do I sound now?")
                else:
                    speak("Sorry, only one voice is available on this system.")
            
            # Basic greetings and responses
            elif any(phrase in query for phrase in ['are you there', 'hello jarvis', 'hi jarvis']):
                speak("Yes, I'm here and ready to help!")
            
            elif 'who made you' in query or 'who created you' in query:
                speak("I was created as a secure, privacy-focused voice assistant to help with daily tasks while keeping your data safe and local.")
            
            # Website navigation
            elif 'open youtube' in query:
                self.open_website('https://www.youtube.com')
                speak("Opening YouTube")
            
            elif 'open google' in query:
                self.open_website('https://www.google.com')
                speak("Opening Google")
            
            elif 'open github' in query:
                self.open_website('https://www.github.com')
                speak("Opening GitHub")
            
            # YouTube search
            elif 'search youtube' in query:
                speak('What would you like to search for on YouTube?')
                search_term = take_command()
                if search_term and search_term != 'none':
                    youtube_search(search_term)
            
            # Web search
            elif 'search' in query and 'youtube' not in query:
                speak('What would you like to search for?')
                search_term = take_command()
                if search_term and search_term != 'none':
                    self.search_web(search_term)
            
            # Location search
            elif 'location' in query or 'find place' in query:
                speak('What location would you like to find?')
                location = take_command()
                if location and location != 'none':
                    self.search_maps(location)
            
            # Time
            elif 'time' in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {current_time}")
            
            # Date
            elif 'date' in query:
                current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today is {current_date}")
            
            # System information
            elif 'cpu' in query or 'system info' in query:
                cpu_info = get_cpu_info()
                speak(cpu_info)
            
            # Screenshot
            elif 'screenshot' in query:
                speak("Taking a screenshot")
                screenshot()
            
            # Joke
            elif 'joke' in query:
                tell_joke()
            
            # Notes
            elif 'remember' in query:
                speak("What should I remember?")
                note = take_command()
                if note and note != 'none':
                    self.remember_note(note)
            
            elif 'recall' in query or 'what do you remember' in query:
                self.recall_notes()
            
            # Dictionary
            elif 'dictionary' in query or 'define' in query:
                speak('What word would you like me to look up?')
                word = take_command()
                if word and word != 'none':
                    lookup_word(word)
            
            # News
            elif 'news' in query:
                speak('Getting the latest news headlines...')
                speak_news()
                speak('Would you like to read more details?')
                response = take_command()
                if response and 'yes' in response.lower():
                    news_url = get_news_url()
                    if news_url:
                        self.open_website(news_url)
            
            # Email
            elif 'send email' in query:
                speak('To whom should I send the email?')
                recipient = take_command()
                if recipient and recipient != 'none':
                    speak('What should I write in the email?')
                    content = take_command()
                    if content and content != 'none':
                        success = send_email(recipient, content)
                        if success:
                            speak('Email sent successfully!')
                        else:
                            speak('Sorry, I could not send the email.')
            
            # Exit
            elif any(phrase in query for phrase in ['exit', 'quit', 'goodbye', 'bye']):
                speak("Goodbye! Have a great day!")
                return False
            
            # Unknown command
            else:
                speak("I'm sorry, I didn't understand that command. Could you please try again?")
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            speak("Sorry, I encountered an error processing your request.")
        
        return True
    
    def run(self):
        """Main execution loop for JARVIS."""
        logger.info("Starting JARVIS...")
        
        # Optional: Face recognition authentication
        # Uncomment the following lines to enable face recognition
        # if not authenticate_user():
        #     speak("Authentication failed. Goodbye.")
        #     return
        
        self.wish_user()
        
        while True:
            try:
                query = take_command()
                
                if query and query.lower() != 'none':
                    if not self.execute_command(query):
                        break
                else:
                    # Handle silence or unrecognized speech
                    continue
                    
            except KeyboardInterrupt:
                speak("Goodbye!")
                logger.info("JARVIS stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                speak("I encountered an unexpected error. Please try again.")


if __name__ == "__main__":
    try:
        jarvis = JARVIS()
        jarvis.run()
    except Exception as e:
        logging.error(f"Failed to start JARVIS: {e}")
        print(f"Error starting JARVIS: {e}")