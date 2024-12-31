"""
Custom error types for the audiobook converter
"""
from typing import Optional

ERROR_CODES = {
    # PDF Processing Errors
    'PDF_NOT_FOUND': "PDF file not found",
    'PDF_CORRUPTED': "PDF file is corrupted or invalid",
    'PDF_NOT_LOADED': "No PDF file has been loaded",
    'PAGE_NOT_FOUND': "Page number is out of range",
    'TEXT_EXTRACTION_ERROR': "Failed to extract text from page",
    'PDF_CLEANUP_ERROR': "Error during PDF cleanup",
    
    # Text-to-Speech Errors
    'TTS_ENGINE_ERROR': "Text-to-speech engine error",
    'TTS_SPEAK_ERROR': "Failed to speak text",
    'TTS_RATE_ERROR': "Invalid speech rate",
    'TTS_VOLUME_ERROR': "Invalid volume level",
    'TTS_VOICE_ERROR': "Error setting or getting voices",
    
    # UI Errors
    'UI_ERROR': "User interface error",
    'INVALID_PAGE_NUMBER': "Invalid page number",
    'INVALID_SPEED': "Invalid reading speed",
    'INVALID_VOLUME': "Invalid volume level"
}

class AudiobookError(Exception):
    """Base error class for audiobook converter"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class PDFProcessingError(AudiobookError):
    """Error in PDF processing"""
    pass

class TextToSpeechError(AudiobookError):
    """Error in text-to-speech conversion"""
    pass

class UIError(AudiobookError):
    """Error in user interface"""
    pass
