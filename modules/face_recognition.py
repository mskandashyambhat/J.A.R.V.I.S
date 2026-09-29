"""
Privacy-focused face recognition module for JARVIS
Includes user consent, local data storage, and secure authentication features.
"""

import cv2
import os
import logging
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from .helpers import speak, create_data_directory

logger = logging.getLogger(__name__)

class PrivacyAwareFaceRecognition:
    """
    Privacy-focused face recognition system with user consent and local storage.
    All biometric data stays local and is never transmitted anywhere.
    """
    
    def __init__(self):
        """Initialize the face recognition system with privacy protections."""
        self.data_dir = create_data_directory()
        self.face_data_dir = self.data_dir / 'face_data'
        self.face_data_dir.mkdir(exist_ok=True)
        
        # Face recognition files
        self.trainer_file = self.face_data_dir / 'trainer.yml'
        self.cascade_file = self.face_data_dir / 'haarcascade_frontalface_default.xml'
        self.user_data_file = self.face_data_dir / 'users.txt'
        self.consent_file = self.data_dir / 'face_recognition_consent.txt'
        
        # Initialize components
        self.recognizer = None
        self.face_cascade = None
        self.users = {}
        self.next_user_id = 1
        
        # Privacy settings
        self.max_failed_attempts = 3
        self.recognition_threshold = 50  # Lower is more strict
        
        logger.info("Privacy-aware face recognition system initialized")
    
    def _check_opencv_availability(self) -> bool:
        """Check if OpenCV and face recognition modules are available."""
        try:
            # Test if cv2.face is available
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            return True
        except AttributeError:
            logger.error("cv2.face module not available. Please install opencv-contrib-python")
            return False
        except Exception as e:
            logger.error(f"Error initializing face recognition: {e}")
            return False
    
    def _setup_cascade_classifier(self) -> bool:
        """Set up the Haar cascade classifier for face detection."""
        try:
            # First try to use the local cascade file
            if self.cascade_file.exists():
                self.face_cascade = cv2.CascadeClassifier(str(self.cascade_file))
                if not self.face_cascade.empty():
                    return True
            
            # Try to use OpenCV's built-in cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                if not self.face_cascade.empty():
                    # Copy to local directory for future use
                    import shutil
                    shutil.copy2(cascade_path, self.cascade_file)
                    return True
            
            logger.error("Could not load face cascade classifier")
            return False
            
        except Exception as e:
            logger.error(f"Error setting up cascade classifier: {e}")
            return False
    
    def _load_user_data(self) -> None:
        """Load user data from local storage."""
        try:
            if self.user_data_file.exists():
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if ':' in line:
                            user_id, name = line.strip().split(':', 1)
                            self.users[int(user_id)] = name
                            self.next_user_id = max(self.next_user_id, int(user_id) + 1)
            
            logger.info(f"Loaded {len(self.users)} users from local storage")
            
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            self.users = {}
    
    def _save_user_data(self) -> None:
        """Save user data to local storage."""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                for user_id, name in self.users.items():
                    f.write(f"{user_id}:{name}\n")
            
            logger.info("User data saved to local storage")
            
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
    
    def check_consent(self) -> bool:
        """
        Check if user has given consent for biometric data processing.
        
        Returns:
            True if consent given, False otherwise
        """
        try:
            if self.consent_file.exists():
                with open(self.consent_file, 'r', encoding='utf-8') as f:
                    consent = f.read().strip().lower()
                    return consent == 'yes'
            return False
            
        except Exception as e:
            logger.error(f"Error checking consent: {e}")
            return False
    
    def request_consent(self) -> bool:
        """
        Request user consent for biometric data processing.
        
        Returns:
            True if consent given, False otherwise
        """
        try:
            speak("JARVIS can use face recognition for secure authentication.")
            speak("This feature will:")
            speak("1. Store your facial data locally on your device only")
            speak("2. Never transmit your biometric data anywhere")
            speak("3. Allow you to delete all data at any time")
            speak("4. Use your camera only during authentication")
            
            speak("Do you consent to use face recognition? Please say yes or no.")
            
            # In a real implementation, you'd get voice input here
            # For now, we'll prompt via console
            print("\nFace Recognition Consent Request:")
            print("Do you consent to use face recognition for authentication?")
            print("Your biometric data will be stored locally and never transmitted.")
            print("Type 'yes' to consent or 'no' to decline:")
            
            response = input().strip().lower()
            
            # Save consent response
            with open(self.consent_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            if response == 'yes':
                speak("Thank you for your consent. Setting up face recognition.")
                logger.info("User consented to face recognition")
                return True
            else:
                speak("Face recognition will not be used. You can change this later.")
                logger.info("User declined face recognition consent")
                return False
                
        except Exception as e:
            logger.error(f"Error requesting consent: {e}")
            return False
    
    def setup_new_user(self, name: str = "User") -> bool:
        """
        Set up face recognition for a new user with data collection.
        
        Args:
            name: User name for identification
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            if not self._check_opencv_availability():
                speak("Face recognition is not available on this system.")
                return False
            
            if not self._setup_cascade_classifier():
                speak("Could not initialize face detection. Please check your OpenCV installation.")
                return False
            
            if not self.check_consent():
                if not self.request_consent():
                    return False
            
            speak(f"Setting up face recognition for {name}")
            speak("Please look at the camera. I'll capture several images of your face.")
            speak("Press 'q' to quit when done, or 's' to save samples.")
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                speak("Could not access camera. Please check camera permissions.")
                logger.error("Could not access camera")
                return False
            
            cap.set(3, 640)  # Width
            cap.set(4, 480)  # Height
            
            user_id = self.next_user_id
            self.users[user_id] = name
            self.next_user_id += 1
            
            # Create directory for face samples
            samples_dir = self.face_data_dir / 'samples'
            samples_dir.mkdir(exist_ok=True)
            
            count = 0
            max_samples = 30
            
            speak("Starting face capture. Look at the camera and move your head slightly.")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.3, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    count += 1
                    
                    # Save face sample
                    face_sample = gray[y:y+h, x:x+w]
                    sample_file = samples_dir / f"user_{user_id}_{count}.jpg"
                    cv2.imwrite(str(sample_file), face_sample)
                    
                    cv2.putText(frame, f"Capturing: {count}/{max_samples}", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                
                cv2.imshow('Face Capture - Press q to quit, s to finish', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or count >= max_samples:
                    break
                elif key == ord('s') and count >= 10:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if count < 10:
                speak("Not enough face samples captured. Please try again.")
                return False
            
            # Train the recognizer
            if self._train_recognizer():
                self._save_user_data()
                speak(f"Face recognition setup complete for {name}. Captured {count} samples.")
                logger.info(f"Face recognition setup complete for user {name} (ID: {user_id})")
                return True
            else:
                speak("Failed to train face recognition model.")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up new user: {e}")
            speak("An error occurred during face recognition setup.")
            return False
    
    def _train_recognizer(self) -> bool:
        """Train the face recognition model with collected samples."""
        try:
            samples_dir = self.face_data_dir / 'samples'
            if not samples_dir.exists():
                return False
            
            faces = []
            ids = []
            
            # Load all face samples
            for sample_file in samples_dir.glob("user_*.jpg"):
                try:
                    # Extract user ID from filename
                    filename = sample_file.stem
                    user_id = int(filename.split('_')[1])
                    
                    # Load and process image
                    img = cv2.imread(str(sample_file), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        ids.append(user_id)
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse sample file {sample_file}: {e}")
                    continue
            
            if len(faces) == 0:
                logger.error("No face samples found for training")
                return False
            
            # Train the recognizer
            if not self.recognizer:
                self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            self.recognizer.train(faces, np.array(ids))
            self.recognizer.write(str(self.trainer_file))
            
            logger.info(f"Face recognition model trained with {len(faces)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training recognizer: {e}")
            return False
    
    def authenticate_user(self) -> bool:
        """
        Authenticate user using face recognition.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if not self.check_consent():
                logger.info("Face recognition not consented")
                return False
            
            if not self._check_opencv_availability():
                logger.error("Face recognition not available")
                return False
            
            if not self._setup_cascade_classifier():
                logger.error("Could not setup face detection")
                return False
            
            # Load trained model if exists
            if not self.trainer_file.exists():
                speak("No face recognition data found. Please set up face recognition first.")
                return False
            
            try:
                self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                self.recognizer.read(str(self.trainer_file))
                self._load_user_data()
            except Exception as e:
                logger.error(f"Could not load face recognition model: {e}")
                speak("Face recognition model is corrupted. Please set up again.")
                return False
            
            speak("Starting face recognition authentication...")
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                speak("Could not access camera.")
                return False
            
            cap.set(3, 640)
            cap.set(4, 480)
            
            failed_attempts = 0
            max_attempts = 30  # 30 frames to try recognition
            
            for attempt in range(max_attempts):
                ret, frame = cap.read()
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.2, 
                    minNeighbors=5, 
                    minSize=(50, 50)
                )
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Recognize face
                    face_roi = gray[y:y+h, x:x+w]
                    user_id, confidence = self.recognizer.predict(face_roi)
                    
                    # Lower confidence value means better match
                    if confidence < self.recognition_threshold:
                        user_name = self.users.get(user_id, "Unknown")
                        cv2.putText(frame, f"Welcome {user_name}", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        speak(f"Authentication successful. Welcome, {user_name}!")
                        logger.info(f"Face recognition authentication successful for {user_name}")
                        return True
                    else:
                        cv2.putText(frame, "Not recognized", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        failed_attempts += 1
                
                cv2.imshow('Authentication - Press q to quit', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            speak("Face recognition authentication failed.")
            logger.warning("Face recognition authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            speak("An error occurred during authentication.")
            return False
    
    def delete_biometric_data(self) -> bool:
        """
        Delete all biometric data and revoke consent.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            speak("Deleting all biometric data...")
            
            # Remove all face recognition files
            files_to_delete = [
                self.trainer_file,
                self.user_data_file,
                self.consent_file
            ]
            
            for file_path in files_to_delete:
                if file_path.exists():
                    file_path.unlink()
            
            # Remove samples directory
            samples_dir = self.face_data_dir / 'samples'
            if samples_dir.exists():
                import shutil
                shutil.rmtree(samples_dir)
            
            # Clear in-memory data
            self.users = {}
            self.recognizer = None
            
            speak("All biometric data has been deleted from your device.")
            logger.info("All biometric data deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting biometric data: {e}")
            speak("Error occurred while deleting biometric data.")
            return False
    
    def get_privacy_info(self) -> Dict[str, Any]:
        """
        Get privacy information about stored data.
        
        Returns:
            Dictionary with privacy information
        """
        try:
            samples_dir = self.face_data_dir / 'samples'
            sample_count = len(list(samples_dir.glob("*.jpg"))) if samples_dir.exists() else 0
            
            info = {
                'consent_given': self.check_consent(),
                'users_registered': len(self.users),
                'model_trained': self.trainer_file.exists(),
                'sample_images': sample_count,
                'data_location': str(self.face_data_dir),
                'data_encrypted': False,  # Currently not encrypted
                'data_transmitted': False  # Never transmitted
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting privacy info: {e}")
            return {}

# Global face recognition service
_face_recognition_service = PrivacyAwareFaceRecognition()

def authenticate_user() -> bool:
    """
    Authenticate user using face recognition.
    
    Returns:
        True if authentication successful, False otherwise
    """
    return _face_recognition_service.authenticate_user()

def setup_face_recognition(name: str = "User") -> bool:
    """
    Set up face recognition for a new user.
    
    Args:
        name: User name
    
    Returns:
        True if setup successful, False otherwise
    """
    return _face_recognition_service.setup_new_user(name)

def delete_face_data() -> bool:
    """
    Delete all biometric data.
    
    Returns:
        True if successful, False otherwise
    """
    return _face_recognition_service.delete_biometric_data()

def get_face_recognition_status() -> Dict[str, Any]:
    """
    Get face recognition privacy status.
    
    Returns:
        Dictionary with status information
    """
    return _face_recognition_service.get_privacy_info()