# 🤖 JARVIS - Secure Voice Assistant

**J**ust **A** **R**ather **V**ery **I**ntelligent **S**ystem - A privacy-focused, secure voice assistant that keeps your data local.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Security](https://img.shields.io/badge/security-focused-red.svg)
![Privacy](https://img.shields.io/badge/privacy-first-orange.svg)

## 🔒 Security & Privacy Features

This JARVIS implementation prioritizes your security and privacy:

- ✅ **No hardcoded credentials** - All API keys via environment variables
- ✅ **Local data storage only** - Your data never leaves your device
- ✅ **Encrypted email credentials** - Using Fernet encryption with PBKDF2
- ✅ **Biometric data consent** - Explicit user consent for face recognition
- ✅ **Input sanitization** - Protection against injection attacks  
- ✅ **URL validation** - Safe web browsing with malicious URL blocking
- ✅ **Cross-platform security** - Secure defaults for macOS, Linux, and Windows
- ✅ **Activity logging** - Local-only audit trails
- ✅ **Secure file operations** - Proper permissions and error handling

## 🚀 Quick Start

### 1. Clone and Setup
```bash
cd JARVIS
python setup.py
```

The interactive setup will guide you through:
- Installing dependencies
- Creating configuration files
- Setting up API keys
- Configuring features

### 2. Run JARVIS
```bash
python jarvis.py
```

### 3. First Use
- JARVIS will greet you and explain available features
- Optionally set up face recognition for secure authentication
- Start with basic commands like "What time is it?"

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **Microphone** (for voice commands)
- **Speakers/Headphones** (for audio responses)
- **Camera** (optional, for face recognition)

### Supported Platforms
- 🍎 **macOS** (10.14+)
- 🐧 **Linux** (Ubuntu 18.04+, other distros)
- 🪟 **Windows** (10+)

## 🎯 Features

### Core Features (Always Available)
- 🗣️ **Voice Commands** - Natural speech recognition
- 🔊 **Text-to-Speech** - Clear voice responses
- 🕒 **Time & Date** - Current time and date information
- 🌐 **Web Search** - Google/Bing/DuckDuckGo integration
- 📖 **Dictionary** - Word definitions and meanings
- 📝 **Notes** - Remember and recall information
- 🖼️ **Screenshots** - Capture and save screenshots
- 💻 **System Info** - CPU, memory, and battery status

### Enhanced Features (Require Setup)
- 📰 **News Headlines** - Latest news from NewsAPI
- 🌤️ **Weather Information** - Current weather via OpenWeatherMap
- 📧 **Secure Email** - Encrypted email sending
- 🎥 **YouTube Integration** - Search and play videos
- 👤 **Face Recognition** - Biometric authentication
- 📱 **Smart Home Ready** - Extensible architecture

## 🛠️ Installation

### Automated Setup (Recommended)
```bash
python setup.py
```

### Manual Installation

1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **System Dependencies**

**macOS:**
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev espeak
```

**Windows:**
Dependencies usually install automatically. If PyAudio fails:
```bash
pip install pipwin
pipwin install pyaudio
```

3. **Configuration**
```bash
cp .env.example .env
# Edit .env with your preferences and API keys
```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# API Keys (Optional - Features work without them but with limitations)
NEWS_API_KEY=your_newsapi_key_here
OPENWEATHER_API_KEY=your_weather_key_here

# Feature Toggles
ENABLE_FACE_RECOGNITION=false
ENABLE_NEWS=true
ENABLE_WEATHER=true
ENABLE_EMAIL=true

# Voice Settings
VOICE_RATE=150
VOICE_VOLUME=0.9

# Security Settings
LOG_LEVEL=INFO
MAX_FAILED_AUTH_ATTEMPTS=3
```

### Getting API Keys

#### NewsAPI (Free)
1. Visit [NewsAPI.org](https://newsapi.org/)
2. Sign up for a free account
3. Copy your API key to `NEWS_API_KEY`

#### OpenWeatherMap (Free)
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Copy your API key to `OPENWEATHER_API_KEY`

## 🎤 Voice Commands

### Basic Commands
```
"JARVIS, what time is it?"
"Hello JARVIS"
"What's the date today?"
"Take a screenshot"
"Tell me a joke"
"What's my CPU usage?"
```

### Web & Search
```
"Search for Python tutorials"
"Open YouTube"
"Search YouTube for coding music"
"Open Google"
"Find the location of Tokyo"
```

### Information
```
"What's in the news?"
"What's the weather like?"
"Define artificial intelligence"
"Remember that I have a meeting at 3 PM"
"What do you remember?"
```

### Email (After Setup)
```
"Send an email"
"Add contact John with email john@example.com"
"Send email to John"
```

### System
```
"Switch voice"
"Exit"
"Goodbye"
```

## 🔐 Security Implementation

### Credential Protection
- **Email passwords**: Encrypted with Fernet + PBKDF2HMAC
- **API keys**: Environment variables only, never hardcoded
- **Biometric data**: Local storage with explicit consent
- **File permissions**: Restrictive permissions on sensitive files

### Input Validation
- **Command sanitization**: XSS and injection protection
- **URL validation**: Malicious URL blocking
- **File path validation**: Directory traversal prevention
- **Length limits**: Buffer overflow protection

### Privacy Measures
- **Local-only processing**: No data transmission to third parties
- **Consent-based features**: Explicit permission for biometric data
- **Data retention**: Automatic cleanup of temporary files
- **Audit logging**: Local activity logs for security monitoring

## 🏠 Data Storage

All JARVIS data is stored locally in your home directory:

```
~/.jarvis/
├── config.json          # Settings and preferences
├── jarvis.log           # Activity logs
├── notes.txt            # Your saved notes
├── face_data/           # Face recognition data (if enabled)
│   ├── samples/         # Face samples
│   └── trainer.yml      # Recognition model
├── email_config/        # Email configuration
│   ├── credentials.enc  # Encrypted email credentials
│   └── contacts.json    # Your contacts
└── cache/               # Temporary cache files
    └── word_cache.json  # Dictionary cache
```

## 🔒 Security Best Practices

### For Users
1. **Keep API keys secure** - Never share your .env file
2. **Regular updates** - Keep dependencies updated
3. **Review permissions** - Check what data JARVIS accesses
4. **Backup carefully** - Exclude sensitive data from cloud backups
5. **Monitor logs** - Check jarvis.log for suspicious activity

### For Developers
1. **Input validation** - Always sanitize user input
2. **Secure defaults** - Fail safely when possible
3. **Error handling** - Don't expose sensitive info in errors
4. **Dependency scanning** - Regular security updates
5. **Code review** - Security-focused code reviews

## 🛡️ Privacy Policy

JARVIS is designed with privacy by default:

- ✅ **No data collection**: No analytics, tracking, or telemetry
- ✅ **Local processing**: All computation happens on your device  
- ✅ **No cloud dependency**: Works completely offline (except API features)
- ✅ **User control**: You control all data and can delete it anytime
- ✅ **Transparency**: Open source - audit the code yourself
- ✅ **Minimal permissions**: Only requests necessary system access

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'cv2'"**
```bash
pip install opencv-contrib-python
```

**"Cannot access microphone"**
- Check microphone permissions in system settings
- Ensure microphone is not used by other applications

**"PyAudio installation failed"**
- macOS: `brew install portaudio`
- Linux: `sudo apt-get install portaudio19-dev`
- Windows: Use `pipwin install pyaudio`

**"Speech recognition not working"**
- Check internet connection (Google Speech API requires internet)
- Verify microphone is working in other applications
- Check microphone permissions

**"Face recognition setup fails"**
- Ensure camera permissions are granted
- Install opencv-contrib-python: `pip install opencv-contrib-python`
- Check camera is not used by other applications

### Debug Mode
Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python jarvis.py
```

## 🤝 Contributing

Contributions are welcome! Please focus on:

- 🔒 **Security improvements**
- 🛡️ **Privacy enhancements** 
- 🐛 **Bug fixes**
- 📖 **Documentation**
- ✨ **New features** (with security consideration)

### Development Setup
```bash
git clone <your-fork>
cd JARVIS
python -m venv jarvis_env
source jarvis_env/bin/activate  # or `jarvis_env\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### Security Review Process
1. All security-related changes require review
2. Run security tests: `python -m pytest tests/security/`
3. Check for hardcoded secrets: `git diff --check`
4. Validate input sanitization in new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original JARVIS concept inspired by various open-source voice assistants
- Security improvements based on OWASP guidelines
- Privacy design following GDPR principles
- Cross-platform compatibility testing community

## 🔍 Security Disclosure

If you discover a security vulnerability, please:

1. **Do NOT** create a public issue
2. Email security concerns to [your-security-email]
3. Allow reasonable time for patching before disclosure
4. Provide clear reproduction steps

We take security seriously and will respond promptly to legitimate concerns.

## 🆘 Support

- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Bug Reports**: Create an issue with detailed reproduction steps
- 💡 **Feature Requests**: Open an issue with [FEATURE] tag
- 💬 **Discussions**: Use GitHub Discussions for general questions

## 🚀 Roadmap

### Planned Features
- [ ] Plugin architecture for custom commands
- [ ] Home automation integration (Home Assistant, OpenHAB)
- [ ] Multiple language support
- [ ] Advanced NLP with local models
- [ ] Encrypted cloud sync (optional)
- [ ] Mobile companion app

### Security Roadmap  
- [ ] Hardware security module integration
- [ ] Advanced threat detection
- [ ] Penetration testing automation
- [ ] Security audit tooling
- [ ] Formal security certification

---

## ⚠️ Important Security Notes

1. **This is a replica/educational project** - Not affiliated with the original JARVIS
2. **Regular security updates** - Keep dependencies updated
3. **Review code changes** - Understand what you're running
4. **Backup strategy** - Secure backups of your configuration
5. **Network security** - Consider firewall rules for API access

**🔐 Remember: Your security and privacy are in your hands. JARVIS helps, but you're responsible for keeping your system secure.**