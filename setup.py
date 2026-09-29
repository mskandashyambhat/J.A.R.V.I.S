#!/usr/bin/env python3
"""
JARVIS Setup Script
Interactive setup for the secure JARVIS voice assistant.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: JARVIS requires Python 3.8 or higher")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def detect_system():
    """Detect the operating system."""
    system = platform.system().lower()
    print(f"✅ Detected system: {system}")
    return system

def install_dependencies():
    """Install required Python packages."""
    print("\n🔧 Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_system_dependencies():
    """Set up system-specific dependencies."""
    system = platform.system().lower()
    
    print(f"\n🔧 Setting up system dependencies for {system}...")
    
    if system == "darwin":  # macOS
        print("📝 For macOS, you may need to install:")
        print("   brew install portaudio")
        print("   This is required for voice recognition to work properly")
        
    elif system == "linux":
        print("📝 For Linux, you may need to install:")
        print("   sudo apt-get update")
        print("   sudo apt-get install python3-pyaudio portaudio19-dev espeak")
        print("   These are required for voice recognition and text-to-speech")
        
    elif system == "windows":
        print("📝 For Windows, audio dependencies should install automatically")
        print("   If you encounter issues with PyAudio, try:")
        print("   pip install pipwin")
        print("   pipwin install pyaudio")
    
    input("\nPress Enter after installing system dependencies (or if already installed)...")
    return True

def create_env_file():
    """Create environment file from template."""
    env_file = Path(".env")
    env_template = Path(".env.example")
    
    if env_file.exists():
        response = input(f"\n📄 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    if env_template.exists():
        try:
            content = env_template.read_text()
            env_file.write_text(content)
            print("✅ Created .env file from template")
            print("📝 Edit .env file to add your API keys and preferences")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ .env.example template not found")
        return False

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    home_dir = Path.home()
    jarvis_dir = home_dir / '.jarvis'
    
    try:
        jarvis_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = ['logs', 'face_data', 'email_config', 'cache']
        for subdir in subdirs:
            (jarvis_dir / subdir).mkdir(exist_ok=True)
        
        print(f"✅ JARVIS data directory created at: {jarvis_dir}")
        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False

def test_basic_functionality():
    """Test basic JARVIS functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test imports
        import pyttsx3
        import speech_recognition as sr
        
        # Test TTS
        engine = pyttsx3.init()
        print("✅ Text-to-speech engine initialized")
        
        # Test speech recognition
        r = sr.Recognizer()
        print("✅ Speech recognition initialized")
        
        # Test microphone (optional)
        try:
            with sr.Microphone() as source:
                print("✅ Microphone access available")
        except Exception:
            print("⚠️  Microphone access not available (voice commands won't work)")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Some dependencies may not be installed correctly")
        return False
    except Exception as e:
        print(f"⚠️  Warning: {e}")
        return True  # Continue setup even with warnings

def configure_features():
    """Interactive feature configuration."""
    print("\n⚙️  Feature Configuration")
    print("You can enable/disable features now or later by editing the .env file")
    
    features = {
        'face_recognition': "Face Recognition (requires camera)",
        'news': "News Headlines (requires NewsAPI key)",
        'weather': "Weather Information (requires OpenWeather API key)", 
        'email': "Email Functionality"
    }
    
    config = {}
    
    for feature, description in features.items():
        while True:
            response = input(f"Enable {description}? (y/n/skip): ").lower()
            if response in ['y', 'yes']:
                config[feature] = True
                break
            elif response in ['n', 'no']:
                config[feature] = False
                break
            elif response in ['s', 'skip']:
                break
            else:
                print("Please enter y, n, or skip")
    
    # Update .env file with selections
    try:
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            
            for feature, enabled in config.items():
                env_var = f"ENABLE_{feature.upper()}"
                value = "true" if enabled else "false"
                
                # Update or add the environment variable
                if env_var in content:
                    # Replace existing line
                    import re
                    pattern = rf"^# ?{env_var}=.*$"
                    replacement = f"{env_var}={value}"
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    # Add new line
                    content += f"\n{env_var}={value}\n"
            
            env_file.write_text(content)
            print("✅ Feature configuration saved to .env")
        
    except Exception as e:
        print(f"⚠️  Could not update .env file: {e}")
    
    return True

def display_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*60)
    print("🎉 JARVIS Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file to add API keys for enhanced features:")
    print("   - NewsAPI key for news headlines")
    print("   - OpenWeather API key for weather information")
    
    print("\n2. Run JARVIS:")
    print("   python jarvis.py")
    
    print("\n3. Optional: Set up face recognition on first run")
    
    print("\n📚 Documentation:")
    print("   - README.md contains detailed setup and usage instructions")
    print("   - All your data stays local and secure")
    
    print("\n🔒 Security Features:")
    print("   - No hardcoded credentials")
    print("   - Encrypted email storage")
    print("   - Local-only biometric data")
    print("   - Privacy-focused design")
    
    print("\n⚡ Quick Test:")
    print('   Try saying "JARVIS, what time is it?" after starting')
    
    print("\n" + "="*60)

def main():
    """Main setup function."""
    print("🤖 JARVIS Setup - Secure Voice Assistant")
    print("="*50)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    system = detect_system()
    
    # Setup steps
    steps = [
        ("Installing Python dependencies", install_dependencies),
        ("Setting up system dependencies", setup_system_dependencies),
        ("Creating environment file", create_env_file),
        ("Setting up directories", setup_directories),
        ("Testing basic functionality", test_basic_functionality),
        ("Configuring features", configure_features),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"Step: {step_name}")
        print('='*60)
        
        try:
            if not step_func():
                print(f"❌ Setup step failed: {step_name}")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Setup aborted")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\n❌ Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {step_name}: {e}")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    display_next_steps()

if __name__ == "__main__":
    main()