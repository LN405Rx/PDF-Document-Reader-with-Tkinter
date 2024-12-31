"""
PDF processing module for text-to-speech conversion
"""
import pdfplumber
import logging
from pathlib import Path
from typing import Optional, Dict
from errors import PDFProcessingError, ERROR_CODES

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, file_path: str = None):
        """Initialize PDF processor with optional file path"""
        self.current_pdf: Optional[pdfplumber.PDF] = None
        self.text_cache: Dict[int, str] = {}
        
        if file_path:
            self.load_pdf(file_path)
        
    def load_pdf(self, file_path: str) -> None:
        """Load and validate a PDF file"""
        try:
            # Close any previously opened PDF
            if self.current_pdf:
                self.current_pdf.close()
                self.text_cache.clear()
            
            # Convert to Path object and validate
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise PDFProcessingError(ERROR_CODES['PDF_NOT_FOUND'])
                
            # Open and validate PDF
            self.current_pdf = pdfplumber.open(pdf_path)
            if not self.current_pdf.pages:
                raise PDFProcessingError("PDF file is empty")
                
            logger.info(f"Successfully loaded PDF: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {str(e)}")
            if self.current_pdf:
                self.current_pdf.close()
                self.current_pdf = None
            raise PDFProcessingError(ERROR_CODES['PDF_CORRUPTED'], str(e))
            
    def get_total_pages(self) -> int:
        """Get the total number of pages in the loaded PDF"""
        if not self.current_pdf:
            raise PDFProcessingError(ERROR_CODES['PDF_NOT_LOADED'])
        return len(self.current_pdf.pages)
        
    def extract_text(self, page_num: int) -> str:
        """Extract text from a specific page"""
        try:
            if not self.current_pdf:
                raise PDFProcessingError(ERROR_CODES['PDF_NOT_LOADED'])
                
            # Check if text is cached
            if page_num in self.text_cache:
                return self.text_cache[page_num]
                
            # Validate page number
            if not 0 <= page_num < len(self.current_pdf.pages):
                raise PDFProcessingError(ERROR_CODES['PAGE_NOT_FOUND'])
                
            # Extract text
            page = self.current_pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                return "Page is empty or contains no readable text."
                
            # Cache the text
            self.text_cache[page_num] = text
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from page {page_num}: {str(e)}")
            raise PDFProcessingError(ERROR_CODES['TEXT_EXTRACTION_ERROR'], str(e))
            
    def close(self) -> None:
        """Close the PDF file and clear cache"""
        try:
            if self.current_pdf:
                self.current_pdf.close()
                self.current_pdf = None
            self.text_cache.clear()
        except Exception as e:
            logger.error(f"Error during PDF cleanup: {str(e)}")
            raise PDFProcessingError(ERROR_CODES['PDF_CLEANUP_ERROR'], str(e))
