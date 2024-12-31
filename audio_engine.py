"""
Audio engine module for text-to-speech conversion
"""
from typing import Optional, Dict, Any
import pyttsx3
import logging
from errors import TextToSpeechError, ERROR_CODES

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self):
        self._engine: Optional[pyttsx3.Engine] = None
        self._current_rate: int = 200
        self._current_volume: float = 1.0
        self.initialize_engine()
        
    def initialize_engine(self) -> None:
        """Initialize the text-to-speech engine"""
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self._current_rate)
            self._engine.setProperty('volume', self._current_volume)
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_ENGINE_FAILED'], str(e))
            
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices for the engine"""
        if not self._engine:
            raise TextToSpeechError("TTS engine not initialized")
        return {voice.id: voice for voice in self._engine.getProperty('voices')}
        
    def set_voice(self, voice_id: str) -> None:
        """Set the voice for text-to-speech"""
        try:
            if not self._engine:
                raise TextToSpeechError("TTS engine not initialized")
            self._engine.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
        except Exception as e:
            logger.error(f"Failed to set voice: {str(e)}")
            raise TextToSpeechError("Failed to set voice", str(e))
            
    def set_rate(self, rate: int) -> None:
        """Set the speech rate"""
        if not self._engine:
            raise TextToSpeechError("TTS engine not initialized")
        self._current_rate = rate
        self._engine.setProperty('rate', rate)
        
    def set_volume(self, volume: float) -> None:
        """Set the speech volume"""
        if not self._engine:
            raise TextToSpeechError("TTS engine not initialized")
        self._current_volume = volume
        self._engine.setProperty('volume', volume)
        
    def speak_text(self, text: str) -> None:
        """Convert text to speech"""
        try:
            if not self._engine:
                raise TextToSpeechError("TTS engine not initialized")
            if not text.strip():
                logger.warning("Empty text provided for TTS")
                return
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS processing failed: {str(e)}")
            raise TextToSpeechError(ERROR_CODES['TTS_PROCESSING_FAILED'], str(e))
            
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self._engine:
                self._engine.stop()
            logger.info("Audio engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            
    def __del__(self):
        self.cleanup()
