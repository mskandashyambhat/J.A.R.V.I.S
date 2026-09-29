"""
Secure helper functions for JARVIS
Includes speech, weather, system info, and other utility functions with proper error handling.
"""

import pyttsx3
import pyautogui
import psutil
import pyjokes
import speech_recognition as sr
import requests
import geocoder
import platform
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Global TTS engine
_engine = None

def get_tts_engine():
    """Get or initialize the text-to-speech engine."""
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            voices = _engine.getProperty('voices')
            if voices:
                _engine.setProperty('voice', voices[0].id)
            
            # Set reasonable speech rate
            rate = _engine.getProperty('rate')
            _engine.setProperty('rate', rate - 50)  # Slow down a bit
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            _engine = None
    return _engine

def speak(text: str) -> None:
    """
    Convert text to speech safely.
    
    Args:
        text: Text to speak
    """
    try:
        engine = get_tts_engine()
        if engine:
            engine.say(text)
            engine.runAndWait()
        else:
            # Fallback: print to console if TTS fails
            print(f"JARVIS: {text}")
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        print(f"JARVIS: {text}")

def take_command() -> str:
    """
    Listen for voice input and convert to text.
    
    Returns:
        Recognized speech as string, or 'none' if not understood
    """
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.pause_threshold = 1
            r.energy_threshold = 300
            
            # Listen for audio
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        
        print("Recognizing...")
        # Use Google's speech recognition
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}")
        return query.lower()
        
    except sr.UnknownValueError:
        print("Could not understand audio")
        return "none"
    except sr.RequestError as e:
        logger.error(f"Speech recognition request failed: {e}")
        speak("Sorry, my speech recognition service is currently unavailable.")
        return "none"
    except sr.WaitTimeoutError:
        print("Listening timeout")
        return "none"
    except Exception as e:
        logger.error(f"Error in speech recognition: {e}")
        return "none"

def get_weather() -> Optional[str]:
    """
    Get current weather information using a free weather API.
    
    Returns:
        Weather information string or None if unavailable
    """
    try:
        # Try to get location
        g = geocoder.ip('me')
        if not g.ok:
            return None
        
        lat, lon = g.latlng
        
        # Use OpenWeatherMap free API (requires API key in environment)
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            logger.info("No weather API key found. Weather feature disabled.")
            return None
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('cod') == 200:
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            
            location = data.get('name', 'your location')
            temp = main.get('temp', 'unknown')
            description = weather.get('description', 'unknown conditions')
            humidity = main.get('humidity', 'unknown')
            wind_speed = wind.get('speed', 'unknown')
            
            weather_info = (
                f"Current weather in {location}: {temp}°C with {description}. "
                f"Humidity is {humidity}% and wind speed is {wind_speed} m/s."
            )
            
            return weather_info
        
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
    
    return None

def screenshot() -> bool:
    """
    Take a screenshot and save it to the user's desktop.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create screenshots directory in user's home
        screenshots_dir = Path.home() / 'Desktop' / 'JARVIS_Screenshots'
        screenshots_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = screenshots_dir / f"screenshot_{timestamp}.png"
        
        # Take screenshot
        screenshot_img = pyautogui.screenshot()
        screenshot_img.save(filename)
        
        speak(f"Screenshot saved to {filename}")
        logger.info(f"Screenshot saved: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        speak("Sorry, I couldn't take a screenshot.")
        return False

def get_cpu_info() -> str:
    """
    Get system CPU and battery information.
    
    Returns:
        System information string
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        info = f"CPU usage is {cpu_percent}%. Memory usage is {memory.percent}%."
        
        # Try to get battery info (may not be available on all systems)
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not plugged in"
                info += f" Battery is at {battery_percent}% and is {plugged}."
        except (AttributeError, NotImplementedError):
            # Battery info not available on this system
            pass
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return "Sorry, I couldn't get system information."

def tell_joke() -> None:
    """Tell a random programming joke."""
    try:
        joke = pyjokes.get_joke(language='en', category='all')
        speak(joke)
    except Exception as e:
        logger.error(f"Error getting joke: {e}")
        speak("Why do programmers prefer dark mode? Because light attracts bugs!")

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with system information
    """
    try:
        info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'ram': f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB"
        }
        return info
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}

def safe_file_operation(file_path: Path, operation: str, content: str = None) -> bool:
    """
    Perform file operations safely with proper error handling.
    
    Args:
        file_path: Path to the file
        operation: 'read', 'write', or 'append'
        content: Content to write/append (required for write/append)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if operation == 'read':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif operation == 'write':
            if content is None:
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        elif operation == 'append':
            if content is None:
                return False
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            logger.error(f"Invalid file operation: {operation}")
            return False
            
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return False
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error in file operation: {e}")
        return False

def validate_url(url: str) -> bool:
    """
    Validate if a URL is safe to open.
    
    Args:
        url: URL to validate
    
    Returns:
        True if URL appears safe, False otherwise
    """
    try:
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # Check for valid scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check for valid netloc
        if not parsed.netloc:
            return False
        
        # Basic blacklist (can be extended)
        dangerous_domains = ['localhost', '127.0.0.1', '0.0.0.0']
        if any(domain in parsed.netloc.lower() for domain in dangerous_domains):
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return False

def create_data_directory() -> Path:
    """
    Create and return the JARVIS data directory.
    
    Returns:
        Path to the JARVIS data directory
    """
    data_dir = Path.home() / '.jarvis'
    data_dir.mkdir(exist_ok=True)
    return data_dir

def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent basic injection attacks.
    
    Args:
        user_input: Raw user input
    
    Returns:
        Sanitized input
    """
    if not isinstance(user_input, str):
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '`', '|', ';', '&&', '||']
    sanitized = user_input
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    return sanitized[:500].strip()

def log_user_activity(activity: str) -> None:
    """
    Log user activity for debugging purposes (locally only).
    
    Args:
        activity: Description of the activity
    """
    try:
        data_dir = create_data_directory()
        activity_log = data_dir / 'activity.log'
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {activity}\n"
        
        safe_file_operation(activity_log, 'append', log_entry)
        
    except Exception as e:
        logger.error(f"Error logging activity: {e}")