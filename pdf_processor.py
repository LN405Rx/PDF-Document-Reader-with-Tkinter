"""
PDF processing module for the audiobook converter
"""
from typing import List, Dict, Generator, Optional
import pdfplumber
from pathlib import Path
import logging
from errors import PDFProcessingError, ERROR_CODES

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, chunk_size: int = 10):
        self.chunk_size = chunk_size
        self.current_pdf: Optional[pdfplumber.PDF] = None
        self.cache: Dict[int, str] = {}
        
    def load_pdf(self, file_path: str) -> None:
        """Load a PDF file and validate it"""
        try:
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise PDFProcessingError(ERROR_CODES['PDF_NOT_FOUND'])
                
            self.current_pdf = pdfplumber.open(pdf_path)
            logger.info(f"Successfully loaded PDF: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {str(e)}")
            raise PDFProcessingError(ERROR_CODES['PDF_CORRUPTED'], str(e))
            
    def get_total_pages(self) -> int:
        """Get the total number of pages in the loaded PDF"""
        if not self.current_pdf:
            raise PDFProcessingError("No PDF file loaded")
        return len(self.current_pdf.pages)
        
    def extract_text_chunk(self, start_page: int) -> Generator[str, None, None]:
        """Extract text from PDF in chunks"""
        if not self.current_pdf:
            raise PDFProcessingError("No PDF file loaded")
            
        end_page = min(start_page + self.chunk_size, len(self.current_pdf.pages))
        
        for page_num in range(start_page, end_page):
            try:
                if page_num in self.cache:
                    yield self.cache[page_num]
                    continue
                    
                page = self.current_pdf.pages[page_num]
                text = page.extract_text()
                self.cache[page_num] = text
                yield text
                
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num}: {str(e)}")
                raise PDFProcessingError(f"Failed to extract text from page {page_num}", str(e))
                
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.current_pdf:
                self.current_pdf.close()
            self.cache.clear()
            logger.info("PDF processor cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            
    def __del__(self):
        self.cleanup()
