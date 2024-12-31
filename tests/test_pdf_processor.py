"""
Tests for PDF processor module
"""
import unittest
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_processor import PDFProcessor
from errors import PDFProcessingError

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()
        self.test_pdf_path = Path(__file__).parent / "test_files" / "test.pdf"
        
    def tearDown(self):
        self.processor.cleanup()
        
    def test_load_nonexistent_pdf(self):
        """Test loading a non-existent PDF file"""
        with self.assertRaises(PDFProcessingError) as context:
            self.processor.load_pdf("nonexistent.pdf")
        self.assertTrue("PDF file was not found" in str(context.exception))
        
    def test_get_total_pages_without_pdf(self):
        """Test getting total pages without loading a PDF"""
        with self.assertRaises(PDFProcessingError) as context:
            self.processor.get_total_pages()
        self.assertTrue("No PDF file loaded" in str(context.exception))
        
if __name__ == '__main__':
    unittest.main()
