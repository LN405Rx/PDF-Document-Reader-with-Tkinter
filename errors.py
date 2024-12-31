"""
Custom exceptions for the PDF to Audiobook converter
"""
from typing import Optional

class AudiobookError(Exception):
    """Base exception for all audiobook-related errors"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(f"{message}: {details}" if details else message)

class PDFProcessingError(AudiobookError):
    """Raised when there's an error processing the PDF file"""
    pass

class TextToSpeechError(AudiobookError):
    """Raised when there's an error with the text-to-speech engine"""
    pass

class ResourceError(AudiobookError):
    """Raised when there's an issue with system resources"""
    pass

class ConfigurationError(AudiobookError):
    """Raised when there's an error in the configuration"""
    pass

class UIError(AudiobookError):
    """Raised when there's an error in the UI components"""
    pass

# Error codes for specific scenarios
ERROR_CODES = {
    'PDF_NOT_FOUND': 'The specified PDF file was not found',
    'PDF_CORRUPTED': 'The PDF file is corrupted or invalid',
    'PDF_ENCRYPTED': 'The PDF file is encrypted and cannot be processed',
    'TTS_ENGINE_FAILED': 'Failed to initialize text-to-speech engine',
    'TTS_PROCESSING_FAILED': 'Failed to process text through TTS engine',
    'MEMORY_EXCEEDED': 'System memory usage exceeded threshold',
    'DISK_SPACE_LOW': 'Insufficient disk space for operation',
    'CONFIG_INVALID': 'Invalid configuration detected',
    'UI_COMPONENT_FAILED': 'Failed to create or update UI component'
}
