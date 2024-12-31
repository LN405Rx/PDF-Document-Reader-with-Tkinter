"""
Audio engine module for text-to-speech conversion
"""
import pyttsx3
import logging
from typing import List, Dict
from errors import TextToSpeechError, ERROR_CODES

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 200)
            self.engine.setProperty('volume', 1.0)
            self._voices = None  # Cache for voices
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_ENGINE_ERROR'], str(e))
            
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices"""
        try:
            if self._voices is None:
                self._voices = self.engine.getProperty('voices')
            
            voices = []
            for voice in self._voices:
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                })
            return voices
        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_VOICE_ERROR'], str(e))
            
    def set_voice(self, voice_id: str) -> None:
        """Set the voice by ID"""
        try:
            self.engine.setProperty('voice', voice_id)
        except Exception as e:
            logger.error(f"Failed to set voice: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_VOICE_ERROR'], str(e))
            
    def set_rate(self, rate: int) -> None:
        """Set the speech rate"""
        try:
            if not isinstance(rate, (int, float)) or rate < 100 or rate > 500:
                raise ValueError("Rate must be between 100 and 500")
            self.engine.setProperty('rate', rate)
        except Exception as e:
            logger.error(f"Failed to set rate: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_RATE_ERROR'], str(e))
            
    def set_volume(self, volume: float) -> None:
        """Set the speech volume"""
        try:
            if not isinstance(volume, (int, float)) or volume < 0 or volume > 100:
                raise ValueError("Volume must be between 0 and 100")
            volume = volume / 100.0  # Convert 0-100 to 0-1
            self.engine.setProperty('volume', volume)
        except Exception as e:
            logger.error(f"Failed to set volume: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_VOLUME_ERROR'], str(e))
            
    def speak(self, text: str) -> None:
        """Convert text to speech"""
        try:
            if not text or not text.strip():
                return
                
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Failed to speak text: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_SPEAK_ERROR'], str(e))
            
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.engine.stop()
        except Exception as e:
            logger.error(f"Error during audio engine cleanup: {str(e)}")
            # Don't raise here as this is cleanup code
