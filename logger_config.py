"""
Logging configuration for the application
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import pytz
import os

def setup_logging():
    """Configure logging for the application"""
    try:
        # Get timezone from environment
        tz = pytz.timezone(os.getenv('TIMEZONE', 'America/Chicago'))
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory if it doesn't exist
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set up logging configuration
        logging.basicConfig(
            level=logging.DEBUG,  # Set to DEBUG to see all messages
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),  # Log to console
                logging.FileHandler(  # Log to file
                    filename=log_dir / f"audiobook_{timestamp}.log",
                    mode='w',
                    encoding='utf-8'
                )
            ]
        )
        
        # Disable other loggers
        for logger_name in logging.root.manager.loggerDict:
            if logger_name != __name__:
                logging.getLogger(logger_name).setLevel(logging.WARNING)
                
        logger = logging.getLogger(__name__)
        logger.info("Logging configured successfully")
        
    except Exception as e:
        print(f"Failed to configure logging: {str(e)}")
        raise
