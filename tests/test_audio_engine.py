"""
Tests for audio engine module
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_engine import AudioEngine
from errors import TextToSpeechError

class TestAudioEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AudioEngine()
        
    def tearDown(self):
        self.engine.cleanup()
        
    def test_set_invalid_rate(self):
        """Test setting an invalid speech rate"""
        with self.assertRaises(TextToSpeechError):
            self.engine.set_rate(-1)
            
    def test_set_invalid_volume(self):
        """Test setting an invalid volume"""
        with self.assertRaises(TextToSpeechError):
            self.engine.set_volume(2.0)
            
    def test_speak_empty_text(self):
        """Test speaking empty text"""
        # Should not raise an error, just log a warning
        self.engine.speak_text("")
        
if __name__ == '__main__':
    unittest.main()
