"""
Configuration module for JARVIS
Handles environment variables, settings, and secure configuration management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class JARVISConfig:
    """Secure configuration manager for JARVIS settings."""
    
    def __init__(self):
        """Initialize configuration with secure defaults."""
        # Base directories
        self.home_dir = Path.home()
        self.jarvis_dir = Path(os.getenv('JARVIS_DATA_DIR', self.home_dir / '.jarvis'))
        self.jarvis_dir.mkdir(exist_ok=True)
        
        # Configuration file
        self.config_file = self.jarvis_dir / 'config.json'
        
        # Load configuration
        self._config = self._load_config()
        
        # Load environment variables
        self._load_env_config()
        
        logger.info(f"JARVIS configuration initialized. Data dir: {self.jarvis_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            # Core settings
            'version': '1.0.0',
            'first_run': True,
            'setup_complete': False,
            
            # Feature toggles
            'features': {
                'face_recognition': False,
                'news': False,
                'weather': False,
                'email': False,
                'youtube': True,
                'web_browser': True,
                'dictionary': True
            },
            
            # Voice settings
            'voice': {
                'rate': 150,
                'volume': 0.9,
                'voice_index': 0
            },
            
            # Security settings
            'security': {
                'log_level': 'INFO',
                'max_failed_auth_attempts': 3,
                'require_face_auth': False,
                'log_user_activity': True
            },
            
            # Privacy settings
            'privacy': {
                'data_retention_days': 30,
                'auto_delete_logs': True,
                'minimize_data_collection': True
            },
            
            # Feature-specific settings
            'face_recognition': {
                'threshold': 50,
                'max_samples': 30,
                'camera_index': 0
            },
            
            'news': {
                'country': 'us',
                'category': 'general',
                'max_headlines': 5
            },
            
            'email': {
                'default_provider': 'gmail',
                'signature': '',
                'auto_reply': False
            },
            
            'web': {
                'default_search_engine': 'google',
                'safe_browsing': True,
                'block_suspicious_urls': True
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle new settings
                    self._merge_config(default_config, loaded_config)
                    return default_config
            else:
                return default_config
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return default_config
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> None:
        """Recursively merge loaded config with defaults."""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        try:
            # API Keys
            if os.getenv('NEWS_API_KEY'):
                self._config['features']['news'] = True
            
            if os.getenv('OPENWEATHER_API_KEY'):
                self._config['features']['weather'] = True
            
            # Feature toggles
            env_features = {
                'ENABLE_FACE_RECOGNITION': 'face_recognition',
                'ENABLE_NEWS': 'news',
                'ENABLE_WEATHER': 'weather',
                'ENABLE_EMAIL': 'email'
            }
            
            for env_var, feature in env_features.items():
                value = os.getenv(env_var)
                if value is not None:
                    self._config['features'][feature] = value.lower() == 'true'
            
            # Voice settings
            if os.getenv('VOICE_RATE'):
                try:
                    self._config['voice']['rate'] = int(os.getenv('VOICE_RATE'))
                except ValueError:
                    pass
            
            if os.getenv('VOICE_VOLUME'):
                try:
                    self._config['voice']['volume'] = float(os.getenv('VOICE_VOLUME'))
                except ValueError:
                    pass
            
            # Security settings
            if os.getenv('LOG_LEVEL'):
                self._config['security']['log_level'] = os.getenv('LOG_LEVEL').upper()
            
            if os.getenv('MAX_FAILED_AUTH_ATTEMPTS'):
                try:
                    self._config['security']['max_failed_auth_attempts'] = int(os.getenv('MAX_FAILED_AUTH_ATTEMPTS'))
                except ValueError:
                    pass
            
            # Feature-specific settings
            if os.getenv('FACE_RECOGNITION_THRESHOLD'):
                try:
                    self._config['face_recognition']['threshold'] = int(os.getenv('FACE_RECOGNITION_THRESHOLD'))
                except ValueError:
                    pass
            
            if os.getenv('DEFAULT_NEWS_COUNTRY'):
                self._config['news']['country'] = os.getenv('DEFAULT_NEWS_COUNTRY').lower()
            
            if os.getenv('DEFAULT_EMAIL_PROVIDER'):
                self._config['email']['default_provider'] = os.getenv('DEFAULT_EMAIL_PROVIDER').lower()
            
        except Exception as e:
            logger.error(f"Error loading environment configuration: {e}")
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            # Set restrictive permissions
            try:
                os.chmod(self.config_file, 0o600)
            except (AttributeError, OSError):
                pass  # Windows or permission error
            
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'voice.rate' or 'features.news')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key
            value: Value to set
        
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = key.split('.')
            config_ref = self._config
            
            # Navigate to the parent dictionary
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set the final value
            config_ref[keys[-1]] = value
            return True
        except Exception as e:
            logger.error(f"Error setting configuration value: {e}")
            return False
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature: Feature name
        
        Returns:
            True if enabled, False otherwise
        """
        return self.get(f'features.{feature}', False)
    
    def enable_feature(self, feature: str) -> bool:
        """
        Enable a feature.
        
        Args:
            feature: Feature name
        
        Returns:
            True if successful, False otherwise
        """
        return self.set(f'features.{feature}', True)
    
    def disable_feature(self, feature: str) -> bool:
        """
        Disable a feature.
        
        Args:
            feature: Feature name
        
        Returns:
            True if successful, False otherwise
        """
        return self.set(f'features.{feature}', False)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service from environment variables.
        
        Args:
            service: Service name ('news', 'weather', etc.)
        
        Returns:
            API key or None if not found
        """
        key_map = {
            'news': 'NEWS_API_KEY',
            'weather': 'OPENWEATHER_API_KEY',
            'wordnik': 'WORDNIK_API_KEY'
        }
        
        env_key = key_map.get(service.lower())
        if env_key:
            return os.getenv(env_key)
        return None
    
    def get_data_dir(self) -> Path:
        """Get JARVIS data directory."""
        return self.jarvis_dir
    
    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return self.get('first_run', True)
    
    def mark_setup_complete(self) -> bool:
        """Mark initial setup as complete."""
        success = self.set('first_run', False) and self.set('setup_complete', True)
        if success:
            self.save_config()
        return success
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            
            self._config = self._load_config()
            self.save_config()
            
            logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting configuration: {e}")
            return False
    
    def export_config(self, export_path: Path) -> bool:
        """
        Export configuration to a file (excluding sensitive data).
        
        Args:
            export_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a clean copy without sensitive data
            export_config = self._config.copy()
            
            # Remove any potentially sensitive information
            if 'api_keys' in export_config:
                del export_config['api_keys']
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False

# Global configuration instance
config = JARVISConfig()