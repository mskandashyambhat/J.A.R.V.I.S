"""
Secure email module for JARVIS
Provides encrypted email functionality with secure credential storage and proper authentication.
"""

import smtplib
import ssl
import os
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .helpers import speak, create_data_directory, sanitize_input

logger = logging.getLogger(__name__)

class SecureEmailService:
    """
    Secure email service with encrypted credential storage and safe sending capabilities.
    """
    
    def __init__(self):
        """Initialize the secure email service."""
        self.data_dir = create_data_directory()
        self.email_config_dir = self.data_dir / 'email_config'
        self.email_config_dir.mkdir(exist_ok=True)
        
        self.credentials_file = self.email_config_dir / 'credentials.enc'
        self.contacts_file = self.email_config_dir / 'contacts.json'
        self.settings_file = self.email_config_dir / 'settings.json'
        
        # Email settings
        self.smtp_servers = {
            'gmail': {'server': 'smtp.gmail.com', 'port': 587, 'use_tls': True},
            'outlook': {'server': 'smtp-mail.outlook.com', 'port': 587, 'use_tls': True},
            'yahoo': {'server': 'smtp.mail.yahoo.com', 'port': 587, 'use_tls': True},
            'icloud': {'server': 'smtp.mail.me.com', 'port': 587, 'use_tls': True}
        }
        
        # Load existing configuration
        self.settings = self._load_settings()
        self.contacts = self._load_contacts()
        
        logger.info("Secure email service initialized")
    
    def _generate_key_from_password(self, password: str, salt: bytes) -> bytes:
        """
        Generate encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: Salt for key derivation
        
        Returns:
            Encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_credentials(self, credentials: Dict[str, str], password: str) -> bool:
        """
        Encrypt and store email credentials.
        
        Args:
            credentials: Dictionary with email credentials
            password: Master password for encryption
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate salt and key
            salt = os.urandom(16)
            key = self._generate_key_from_password(password, salt)
            
            # Encrypt credentials
            f = Fernet(key)
            credentials_json = json.dumps(credentials)
            encrypted_data = f.encrypt(credentials_json.encode())
            
            # Store encrypted data with salt
            data_to_store = {
                'salt': base64.b64encode(salt).decode(),
                'encrypted_credentials': base64.b64encode(encrypted_data).decode()
            }
            
            with open(self.credentials_file, 'w') as file:
                json.dump(data_to_store, file, indent=2)
            
            # Set restrictive file permissions (Unix-like systems)
            try:
                os.chmod(self.credentials_file, 0o600)
            except (AttributeError, OSError):
                pass  # Windows or permission error
            
            logger.info("Email credentials encrypted and stored securely")
            return True
            
        except Exception as e:
            logger.error(f"Error encrypting credentials: {e}")
            return False
    
    def _decrypt_credentials(self, password: str) -> Optional[Dict[str, str]]:
        """
        Decrypt stored email credentials.
        
        Args:
            password: Master password for decryption
        
        Returns:
            Decrypted credentials or None if failed
        """
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r') as file:
                stored_data = json.load(file)
            
            # Extract salt and encrypted data
            salt = base64.b64decode(stored_data['salt'])
            encrypted_data = base64.b64decode(stored_data['encrypted_credentials'])
            
            # Generate key and decrypt
            key = self._generate_key_from_password(password, salt)
            f = Fernet(key)
            
            decrypted_data = f.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error decrypting credentials: {e}")
            return None
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load email settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as file:
                    return json.load(file)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        
        return {
            'default_provider': 'gmail',
            'signature': '',
            'auto_reply': False
        }
    
    def _save_settings(self) -> None:
        """Save email settings to file."""
        try:
            with open(self.settings_file, 'w') as file:
                json.dump(self.settings, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def _load_contacts(self) -> Dict[str, str]:
        """Load contacts from file."""
        try:
            if self.contacts_file.exists():
                with open(self.contacts_file, 'r') as file:
                    return json.load(file)
        except Exception as e:
            logger.error(f"Error loading contacts: {e}")
        
        return {}
    
    def _save_contacts(self) -> None:
        """Save contacts to file."""
        try:
            with open(self.contacts_file, 'w') as file:
                json.dump(self.contacts, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving contacts: {e}")
    
    def setup_email_account(self, email: str, password: str, provider: str = 'gmail', master_password: str = None) -> bool:
        """
        Set up email account with encrypted storage.
        
        Args:
            email: Email address
            password: App password or account password
            provider: Email provider ('gmail', 'outlook', 'yahoo', 'icloud')
            master_password: Master password for encryption
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Validate inputs
            email = sanitize_input(email.strip())
            provider = provider.lower().strip()
            
            if '@' not in email or provider not in self.smtp_servers:
                speak("Invalid email address or provider.")
                return False
            
            if not master_password:
                speak("Please provide a master password to encrypt your email credentials.")
                print("Enter master password for credential encryption:")
                master_password = input().strip()
            
            if len(master_password) < 8:
                speak("Master password must be at least 8 characters long.")
                return False
            
            # Test connection first
            smtp_config = self.smtp_servers[provider]
            if not self._test_connection(email, password, smtp_config):
                speak("Could not connect to email server. Please check your credentials.")
                return False
            
            # Encrypt and store credentials
            credentials = {
                'email': email,
                'password': password,
                'provider': provider
            }
            
            if self._encrypt_credentials(credentials, master_password):
                self.settings['default_provider'] = provider
                self._save_settings()
                speak(f"Email account {email} set up successfully with {provider}.")
                logger.info(f"Email account configured for {email}")
                return True
            else:
                speak("Failed to store email credentials securely.")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up email account: {e}")
            speak("An error occurred while setting up the email account.")
            return False
    
    def _test_connection(self, email: str, password: str, smtp_config: Dict[str, Any]) -> bool:
        """
        Test email server connection.
        
        Args:
            email: Email address
            password: Email password
            smtp_config: SMTP configuration
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            
            if smtp_config.get('use_tls'):
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            server.login(email, password)
            server.quit()
            
            logger.info("Email server connection test successful")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Email authentication failed")
            return False
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, master_password: str = None) -> bool:
        """
        Send an email securely.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            master_password: Master password to decrypt credentials
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Sanitize inputs
            to_email = sanitize_input(to_email.strip())
            subject = sanitize_input(subject.strip())
            body = sanitize_input(body)
            
            if '@' not in to_email:
                speak("Invalid recipient email address.")
                return False
            
            if not master_password:
                speak("Please provide your master password to access email credentials.")
                print("Enter master password:")
                master_password = input().strip()
            
            # Decrypt credentials
            credentials = self._decrypt_credentials(master_password)
            if not credentials:
                speak("Could not decrypt email credentials. Please check your master password.")
                return False
            
            # Get SMTP configuration
            provider = credentials['provider']
            smtp_config = self.smtp_servers.get(provider)
            if not smtp_config:
                speak(f"Unknown email provider: {provider}")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = formataddr(('JARVIS Assistant', credentials['email']))
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body and signature
            email_body = body
            if self.settings.get('signature'):
                email_body += f"\n\n{self.settings['signature']}"
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                if smtp_config.get('use_tls'):
                    server.starttls(context=context)
                
                server.login(credentials['email'], credentials['password'])
                server.send_message(msg)
            
            speak(f"Email sent successfully to {to_email}")
            logger.info(f"Email sent to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Email authentication failed")
            speak("Email authentication failed. Please check your credentials.")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            speak("An error occurred while sending the email.")
            return False
    
    def add_contact(self, name: str, email: str) -> bool:
        """
        Add a contact to the address book.
        
        Args:
            name: Contact name
            email: Contact email
        
        Returns:
            True if added successfully, False otherwise
        """
        try:
            name = sanitize_input(name.strip())
            email = sanitize_input(email.strip())
            
            if '@' not in email or not name:
                speak("Invalid contact information.")
                return False
            
            self.contacts[name.lower()] = email
            self._save_contacts()
            
            speak(f"Contact {name} added with email {email}")
            logger.info(f"Contact added: {name} -> {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding contact: {e}")
            speak("Error adding contact.")
            return False
    
    def get_contact_email(self, name: str) -> Optional[str]:
        """
        Get email address for a contact.
        
        Args:
            name: Contact name
        
        Returns:
            Email address or None if not found
        """
        name = name.lower().strip()
        return self.contacts.get(name)
    
    def send_email_to_contact(self, contact_name: str, subject: str, body: str, master_password: str = None) -> bool:
        """
        Send email to a saved contact.
        
        Args:
            contact_name: Name of the contact
            subject: Email subject
            body: Email body
            master_password: Master password for credentials
        
        Returns:
            True if sent successfully, False otherwise
        """
        email = self.get_contact_email(contact_name)
        if not email:
            speak(f"Contact {contact_name} not found in address book.")
            return False
        
        return self.send_email(email, subject, body, master_password)
    
    def list_contacts(self) -> List[str]:
        """
        Get list of saved contacts.
        
        Returns:
            List of contact names
        """
        return list(self.contacts.keys())
    
    def is_configured(self) -> bool:
        """
        Check if email is configured.
        
        Returns:
            True if configured, False otherwise
        """
        return self.credentials_file.exists()
    
    def delete_configuration(self, master_password: str) -> bool:
        """
        Delete email configuration and credentials.
        
        Args:
            master_password: Master password for verification
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Verify master password first
            credentials = self._decrypt_credentials(master_password)
            if not credentials:
                speak("Invalid master password.")
                return False
            
            # Delete files
            if self.credentials_file.exists():
                self.credentials_file.unlink()
            
            speak("Email configuration deleted successfully.")
            logger.info("Email configuration deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting email configuration: {e}")
            speak("Error deleting email configuration.")
            return False

# Global email service
_email_service = SecureEmailService()

def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Send an email to the specified recipient.
    
    Args:
        recipient: Recipient email or contact name
        subject: Email subject
        body: Email body
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not _email_service.is_configured():
        speak("Email is not configured. Please set up your email account first.")
        return False
    
    # Check if recipient is a contact name
    if '@' not in recipient:
        return _email_service.send_email_to_contact(recipient, subject, body)
    else:
        return _email_service.send_email(recipient, subject, body)

def setup_email(email: str, password: str, provider: str = 'gmail') -> bool:
    """
    Set up email account.
    
    Args:
        email: Email address
        password: App password
        provider: Email provider
    
    Returns:
        True if setup successful, False otherwise
    """
    return _email_service.setup_email_account(email, password, provider)

def add_email_contact(name: str, email: str) -> bool:
    """
    Add a contact to the email address book.
    
    Args:
        name: Contact name
        email: Contact email
    
    Returns:
        True if added successfully, False otherwise
    """
    return _email_service.add_contact(name, email)

def list_email_contacts() -> List[str]:
    """
    List all saved email contacts.
    
    Returns:
        List of contact names
    """
    return _email_service.list_contacts()

def is_email_configured() -> bool:
    """
    Check if email is configured.
    
    Returns:
        True if configured, False otherwise
    """
    return _email_service.is_configured()