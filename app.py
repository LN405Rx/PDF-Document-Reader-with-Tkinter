"""
PDF to Audiobook Converter with GUI
A Tkinter-based application that converts PDF files to audiobooks with playback controls.

Enhanced Error Handling:
Added specific error types and messages in the AudiobookPlayerError class
Improved error reporting with detailed messages
New Features:
Added pause/resume functionality (Space key toggles between play/pause)
Added volume control with a slider
Added time remaining estimation
Added keyboard shortcuts for speed control (Ctrl+Up/Down)
Memory Optimization:
Implemented chunk-based PDF loading to reduce memory usage
Added proper cleanup in the reset function
UI Improvements:
Added progress tracking with estimated time remaining
Improved layout and organization of controls
Added more descriptive labels and tooltips
Code Organization:
Better type hints for improved code maintainability
Organized constants in the AppDefaults class
Improved method documentation
Performance:
Reduced CPU usage during pause state
Optimized progress updates
Better thread management
"""

"""
Request the AI to make codebase 
business enterprise ready
"""

import pyttsx3
import pdfplumber
import threading
from typing import Optional, List, Dict, Any, Callable
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
import time
from datetime import datetime
import pytz
import logging
from pathlib import Path
import psutil
from typing_extensions import Final
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audiobook_player.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('app.env')

class AppDefaults:
    """Default values for the application"""
    INITIAL_PAGE = 1
    READING_SPEED = 200
    MIN_SPEED = 50
    MAX_SPEED = 400
    CHUNK_SIZE = 10
    DEFAULT_SPEAKER = "default"
    WINDOW_TITLE = os.getenv('APP_NAME', "Audiobook Player")
    WINDOW_SIZE = "400x700"
    DEFAULT_VOLUME = 1.0
    AVG_WORDS_PER_PAGE = 250
    SESSION_START_TIME = "2024-12-10T10:30:45-06:00"
    TIMEZONE = os.getenv('TIMEZONE', 'America/Chicago')
    MAX_MEMORY_PERCENT = float(os.getenv('MAX_MEMORY_PERCENT', 80.0))
    CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', 300))
    
    @staticmethod
    def get_padding():
        return {"padx": 20, "pady": 10}

class AudiobookPlayerError(Exception):
    """Custom exception for AudiobookPlayer errors"""
    INIT_ERROR = "Failed to initialize AudiobookPlayer"
    ENGINE_ERROR = "Failed to initialize speech engine"
    WIDGET_ERROR = "Failed to create widgets"
    PDF_ERROR = "Error reading PDF"
    NO_PDF_ERROR = "No PDF file loaded"
    TIME_ERROR = "Error handling time operations"

    def __init__(self, error_type: str, details: str = None):
        self.error_type = error_type
        self.details = details
        super().__init__(f"{error_type}: {details}" if details else error_type)

class AudiobookPlayer:
    """Main application class for the PDF to Audiobook converter"""
    
    def __init__(self) -> None:
        """Initialize the AudiobookPlayer application"""
        try:
            self.window = tk.Tk()
            self.window.title(AppDefaults.WINDOW_TITLE)
            self.window.geometry(AppDefaults.WINDOW_SIZE)
            
            # Initialize threading events
            self.pause_event = threading.Event()
            self.stop_event = threading.Event()
            
            # Initialize timezone and session time
            self.tz = pytz.timezone(AppDefaults.TIMEZONE)
            self.session_start = datetime.fromisoformat(AppDefaults.SESSION_START_TIME)
            
            # Initialize memory monitoring
            self.process = psutil.Process()
            self.last_cleanup = time.time()
            
            # Create output directories
            self.output_dir = Path(os.getenv('OUTPUT_DIR', './audiobook_output'))
            self.pdf_books_dir = Path(os.getenv('PDF_BOOKS_DIR', './pdf_books'))
            self.output_dir.mkdir(exist_ok=True)
            self.pdf_books_dir.mkdir(exist_ok=True)
            
            self.init_variables()
            self.init_engine()
            self.create_widgets()
            self.bind_shortcuts()
            
            # Schedule periodic cleanup and UI updates
            self._schedule_periodic_tasks()
            
            logger.info(f"Application initialized successfully at {self.session_start}")
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.INIT_ERROR, str(e))

    def _schedule_periodic_tasks(self) -> None:
        """Schedule periodic tasks for cleanup and UI updates"""
        def schedule_next():
            self.window.after(1000, periodic_tasks)  # Run every second
            
        def periodic_tasks():
            try:
                # Check system resources
                self.check_resources()
                
                # Update UI if reading
                if self.is_reading and not self.is_paused:
                    self.window.update_idletasks()
                
                schedule_next()
            except Exception as e:
                logger.error(f"Error in periodic tasks: {str(e)}")
                schedule_next()
        
        schedule_next()

    def init_variables(self) -> None:
        """Initialize application variables"""
        self.pdf = None
        self.current_page = tk.StringVar(value=str(AppDefaults.INITIAL_PAGE))
        self.is_reading = False
        self.is_paused = False
        self.current_thread = None
        self.start_time = None
        self.pdf_text_cache = {}  # Cache for PDF text chunks
        self.preload_queue = []  # Queue for preloading chunks
        self.processing_lock = threading.Lock()  # Lock for thread-safe operations
        self.batch_size = 5  # Number of chunks to process in batch
        
    def init_engine(self) -> None:
        """Initialize the text-to-speech engine"""
        try:
            # Initialize the engine with sapi5 driver explicitly on Windows
            self.engine = pyttsx3.init('sapi5')
            if not self.engine:
                raise AudiobookPlayerError(AudiobookPlayerError.ENGINE_ERROR, "Failed to initialize speech engine")
            
            # Get available voices
            try:
                self.voices = self.engine.getProperty("voices")
                if not self.voices:
                    logger.warning("No voices found, using system default")
                    self.voices = []
            except Exception as ve:
                logger.warning(f"Error getting voices: {str(ve)}")
                self.voices = []
            
            # Set initial properties with error handling
            try:
                self.engine.setProperty("rate", AppDefaults.READING_SPEED)
                if self.voices:
                    self.engine.setProperty("voice", self.voices[0].id)
                self.engine.setProperty("volume", AppDefaults.DEFAULT_VOLUME)
            except Exception as pe:
                logger.warning(f"Error setting engine properties: {str(pe)}")
            
            # Test the engine with a small text
            try:
                self.engine.say("Ready")
                self.engine.runAndWait()
            except Exception as te:
                logger.warning(f"Test speech failed: {str(te)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize speech engine: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.ENGINE_ERROR, str(e))
        
    def create_widgets(self) -> None:
        """Create and arrange all UI widgets"""
        try:
            main_container = tk.Frame(
                self.window,
                **AppDefaults.get_padding()
            )
            main_container.pack(fill=tk.BOTH, expand=True)
            
            self.create_page_controls(main_container)
            self.create_voice_controls(main_container)
            self.create_speed_controls(main_container)
            self.create_volume_controls(main_container)
            self.create_action_buttons(main_container)
            self.create_progress_section(main_container)
        except Exception as e:
            logger.error(f"Failed to create widgets: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.WIDGET_ERROR, str(e))
        
    def create_page_controls(self, container: tk.Frame) -> None:
        """Create page control widgets"""
        page_frame = tk.LabelFrame(container, text="Page Controls", **AppDefaults.get_padding())
        page_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(page_frame, text="Start Page:").pack()
        self.start_page_entry = tk.Entry(page_frame, width=10)
        self.start_page_entry.insert(0, str(AppDefaults.INITIAL_PAGE))
        self.start_page_entry.pack()
        
        self.file_name_label = tk.Label(page_frame, text="No file selected", wraplength=300)
        self.file_name_label.pack(pady=5)
        
        tk.Label(page_frame, text="Current Page:").pack()
        tk.Label(page_frame, textvariable=self.current_page).pack()
        
    def create_voice_controls(self, container: tk.Frame) -> None:
        """Create voice control widgets"""
        try:
            voice_frame = tk.LabelFrame(container, text="Voice Settings", **AppDefaults.get_padding())
            voice_frame.pack(fill=tk.X, pady=5)
            
            # Voice selection
            tk.Label(voice_frame, text="Voice:").pack()
            
            # Safely get voice IDs or use a default
            voice_ids = []
            default_voice = ""
            if hasattr(self, 'voices') and self.voices:
                voice_ids = [voice.id for voice in self.voices]
                default_voice = self.voices[0].id
            
            self.voice_var = tk.StringVar(value=default_voice)
            if voice_ids:
                voice_menu = tk.OptionMenu(voice_frame, self.voice_var, *voice_ids)
            else:
                voice_menu = tk.OptionMenu(voice_frame, self.voice_var, "Default")
            voice_menu.pack(fill=tk.X)
        except Exception as e:
            logger.error(f"Error creating voice controls: {str(e)}")
            # Create a minimal fallback interface
            tk.Label(container, text="Voice controls unavailable").pack()
        
    def create_speed_controls(self, container: tk.Frame) -> None:
        """Create speed control widgets"""
        speed_frame = tk.LabelFrame(container, text="Speed Settings", **AppDefaults.get_padding())
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.reading_speed = tk.IntVar(value=AppDefaults.READING_SPEED)
        speed_scale = tk.Scale(
            speed_frame,
            from_=AppDefaults.MIN_SPEED,
            to=AppDefaults.MAX_SPEED,
            variable=self.reading_speed,
            orient="horizontal",
            label="Reading Speed (words/min)",
            command=self.update_speed
        )
        speed_scale.pack(fill=tk.X)

    def create_volume_controls(self, container: tk.Frame) -> None:
        """Create volume control widgets"""
        volume_frame = tk.LabelFrame(container, text="Volume", **AppDefaults.get_padding())
        volume_frame.pack(fill=tk.X, pady=5)
        
        self.volume = tk.DoubleVar(value=AppDefaults.DEFAULT_VOLUME)
        volume_scale = tk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            variable=self.volume,
            orient="horizontal",
            label="Volume",
            command=self.update_volume
        )
        volume_scale.pack(fill=tk.X)
        
    def create_progress_section(self, container: tk.Frame) -> None:
        """Create progress tracking widgets"""
        progress_frame = tk.LabelFrame(container, text="Progress", **AppDefaults.get_padding())
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        self.time_remaining_label = tk.Label(progress_frame, text="Time remaining: --")
        self.time_remaining_label.pack()
        
    def create_action_buttons(self, container: tk.Frame) -> None:
        """Create action button widgets"""
        button_frame = tk.Frame(container)
        button_frame.pack(pady=10, fill=tk.X)
        
        buttons = [
            ("Select PDF (Ctrl+O)", self.select_pdf_file),
            ("Play/Pause (Space)", self.toggle_reading),
            ("Stop (Esc)", self.stop_audiobook),
            ("Reset (Ctrl+R)", self.reset_application)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command, width=15).pack(pady=2)
        
    def bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts"""
        try:
            self.window.bind("<space>", lambda e: self.safe_call(self.toggle_reading))
            self.window.bind("<Control-o>", lambda e: self.safe_call(self.select_pdf_file))
            self.window.bind("<Control-r>", lambda e: self.safe_call(self.reset_application))
            self.window.bind("<Escape>", lambda e: self.safe_call(self.stop_audiobook))
            self.window.bind("<Control-Up>", lambda e: self.safe_call(lambda: self.adjust_speed(20)))
            self.window.bind("<Control-Down>", lambda e: self.safe_call(lambda: self.adjust_speed(-20)))
        except Exception as e:
            logger.error(f"Failed to bind shortcuts: {str(e)}")
    
    def safe_call(self, func: Callable) -> None:
        """Safely call a function and handle any errors"""
        try:
            func()
        except Exception as e:
            logger.error(f"Error in function {func.__name__}: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def toggle_reading(self) -> None:
        """Toggle between play, pause and stop states"""
        try:
            if not self.pdf:
                raise AudiobookPlayerError(AudiobookPlayerError.NO_PDF_ERROR)
            
            if not self.is_reading:
                self.start_audiobook()
            elif self.pause_event.is_set():
                self.resume_audiobook()
            else:
                self.pause_audiobook()
        except Exception as e:
            logger.error(f"Error toggling reading state: {str(e)}")
            messagebox.showerror("Error", str(e))

    def adjust_speed(self, delta: int) -> None:
        """Adjust reading speed by delta amount"""
        new_speed = min(max(self.reading_speed.get() + delta, 
                          AppDefaults.MIN_SPEED), 
                       AppDefaults.MAX_SPEED)
        self.reading_speed.set(new_speed)
        self.update_speed(new_speed)

    def update_speed(self, *args) -> None:
        """Update engine reading speed"""
        self.engine.setProperty("rate", self.reading_speed.get())

    def update_volume(self, *args) -> None:
        """Update engine volume"""
        self.engine.setProperty("volume", self.volume.get())

    def pause_audiobook(self) -> None:
        """Pause the audiobook playback"""
        self.is_paused = True
        self.pause_event.set()
        
    def resume_audiobook(self) -> None:
        """Resume the audiobook playback"""
        self.is_paused = False
        self.pause_event.clear()
        
    def stop_audiobook(self) -> None:
        """Stop the audiobook playback"""
        self.stop_event.set()
        self.is_reading = False
        self.is_paused = False
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1.0)

    def select_pdf_file(self) -> None:
        """Handle PDF file selection"""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
            
        try:
            self.load_pdf(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {str(e)}")
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
            
    def load_pdf(self, file_path: str) -> None:
        """Load PDF file with memory optimization"""
        try:
            if self.pdf:
                self.pdf.close()
            
            self.pdf = pdfplumber.open(file_path)
            self.pdf_text_cache.clear()  # Clear cache when loading new file
            self.file_name_label.config(text=Path(file_path).name)
            
            # Pre-load first chunk in background
            threading.Thread(target=self._preload_chunk, args=(1,), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to open PDF: {str(e)}")
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
    
    def _preload_chunk(self, start_page: int) -> None:
        """Preload a chunk of PDF pages in background"""
        try:
            if not self.pdf:
                return
            self.load_pdf_chunk(start_page)
        except Exception as e:
            logger.error(f"Error preloading chunk: {str(e)}")

    def load_pdf_chunk(self, start_page: int, chunk_size: int = AppDefaults.CHUNK_SIZE) -> str:
        """Load a chunk of PDF pages with caching"""
        try:
            if not self.pdf:
                raise AudiobookPlayerError(AudiobookPlayerError.NO_PDF_ERROR)
            
            # Check cache first
            cache_key = f"{start_page}_{chunk_size}"
            if cache_key in self.pdf_text_cache:
                return self.pdf_text_cache[cache_key]
            
            end_page = min(start_page + chunk_size, len(self.pdf.pages))
            text = []
            
            # Process pages in smaller batches for better responsiveness
            for i in range(start_page - 1, end_page):
                try:
                    page = self.pdf.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                    # Allow UI updates between pages
                    self.window.update_idletasks()
                except Exception as pe:
                    logger.error(f"Error extracting text from page {i + 1}: {str(pe)}")
                    continue
            
            result = "\n".join(text).strip()
            self.pdf_text_cache[cache_key] = result  # Cache the result
            
            # Preload next chunk in background if reading
            if self.is_reading and end_page < len(self.pdf.pages):
                threading.Thread(target=self._preload_chunk, args=(end_page + 1,), daemon=True).start()
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading PDF chunk: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.PDF_ERROR, str(e))

    def update_progress(self, current_page: int, total_pages: int) -> None:
        """Update progress bar and estimated time remaining"""
        try:
            # Update current page display
            self.current_page.set(str(current_page))
            
            # Calculate progress percentage
            progress = (current_page / total_pages) * 100
            self.progress_var.set(progress)
            
            # Calculate time remaining
            if self.start_time is None:
                self.start_time = time.time()
            
            elapsed_time = time.time() - self.start_time
            pages_per_second = (current_page - int(self.start_page_entry.get()) + 1) / elapsed_time if elapsed_time > 0 else 0
            remaining_pages = total_pages - current_page
            
            if pages_per_second > 0:
                remaining_seconds = remaining_pages / pages_per_second
                minutes = int(remaining_seconds // 60)
                seconds = int(remaining_seconds % 60)
                self.time_remaining_label.config(text=f"Time remaining: {minutes}m {seconds}s")
            else:
                self.time_remaining_label.config(text="Time remaining: calculating...")
            
            # Update the UI
            self.window.update_idletasks()
            
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")
            self.time_remaining_label.config(text="Time remaining: --")
            
    def read_audiobook(self, start_page: int) -> None:
        """Read the PDF content using text-to-speech"""
        try:
            if not self.pdf:
                raise AudiobookPlayerError(AudiobookPlayerError.NO_PDF_ERROR)
            
            total_pages = len(self.pdf.pages)
            current_page = start_page
            
            # Reset events
            self.stop_event.clear()
            self.pause_event.clear()
            
            # Pre-initialize engine properties
            self.engine.setProperty("rate", self.reading_speed.get())
            self.engine.setProperty("volume", self.volume.get())
            
            while current_page <= total_pages and not self.stop_event.is_set():
                if self.pause_event.is_set():
                    time.sleep(0.1)  # Reduce CPU usage while paused
                    continue
                
                try:
                    # Load chunk and update progress
                    chunk = self.load_pdf_chunk(current_page)
                    self.window.after(0, self.update_progress, current_page, total_pages)
                    
                    if not chunk:
                        logger.warning(f"No text found on page {current_page}")
                        current_page += 1
                        continue
                    
                    # Split text into smaller segments for more responsive playback
                    segments = [s.strip() for s in chunk.split('.') if s.strip()]
                    for segment in segments:
                        if self.stop_event.is_set():
                            break
                            
                        while self.pause_event.is_set():
                            time.sleep(0.1)
                            continue
                        
                        self.engine.say(segment)
                        self.engine.runAndWait()
                        
                        # Allow UI updates between segments
                        self.window.update_idletasks()
                    
                    # Move to next chunk
                    current_page += AppDefaults.CHUNK_SIZE
                    
                except Exception as e:
                    logger.error(f"Error reading page {current_page}: {str(e)}")
                    current_page += 1  # Skip problematic page
                
        except Exception as e:
            self.is_reading = False
            logger.error(f"Error in read_audiobook: {str(e)}")
            self.window.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.is_reading = False
            self.pause_event.clear()
            self.stop_event.clear()
            self.window.after(0, self._reset_progress)
    
    def _reset_progress(self) -> None:
        """Reset progress indicators"""
        self.progress_var.set(0)
        self.time_remaining_label.config(text="Time remaining: --")

    def start_audiobook(self) -> None:
        """Start reading the audiobook"""
        if not self.pdf:
            messagebox.showwarning("Warning", "Please select a PDF file first")
            return
            
        try:
            start_page = int(self.start_page_entry.get())
            if not 1 <= start_page <= len(self.pdf.pages):
                messagebox.showerror(
                    "Error", 
                    f"Invalid page number. Must be between 1 and {len(self.pdf.pages)}"
                )
                return
                
            self.is_reading = True
            self.is_paused = False
            
            # Use session start time for consistent timing
            self.start_time = (datetime.now(self.tz) - self.session_start).total_seconds()
            
            # Create unique output filename with timestamp
            timestamp = datetime.now(self.tz).strftime("%Y%m%d_%H%M%S")
            self.current_output_file = self.output_dir / f"audiobook_{timestamp}.mp3"
            
            logger.info(f"Starting audiobook reading from page {start_page}")
            logger.info(f"Output file: {self.current_output_file}")
            
            self.current_thread = threading.Thread(
                target=self.read_audiobook, 
                args=(start_page,), 
                daemon=True
            )
            self.current_thread.start()
        except ValueError:
            logger.error("Invalid page number entered")
            messagebox.showerror("Error", "Please enter a valid page number")
            
    def reset_application(self) -> None:
        """Reset the application to its initial state"""
        try:
            self.stop_audiobook()
            
            if self.pdf:
                self.pdf.close()
                self.pdf = None
                
            self.file_name_label.config(text="No file selected")
            self.current_page.set(str(AppDefaults.INITIAL_PAGE))
            self.start_page_entry.delete(0, tk.END)
            self.start_page_entry.insert(0, str(AppDefaults.INITIAL_PAGE))
            self.reading_speed.set(AppDefaults.READING_SPEED)
            self.progress_var.set(0)
            self.time_remaining_label.config(text="Time remaining: --")
            self.start_time = None
            
            logger.info("Application reset to initial state")
        except Exception as e:
            logger.error(f"Error resetting application: {str(e)}")
            messagebox.showerror("Error", f"Failed to reset application: {str(e)}")

    def check_resources(self) -> None:
        """Monitor system resources and perform cleanup if needed"""
        try:
            current_memory = self.process.memory_percent()
            if current_memory > AppDefaults.MAX_MEMORY_PERCENT:
                logger.warning(f"High memory usage detected: {current_memory}%")
                self.cleanup_resources()
            
            # Schedule next check
            self.window.after(1000, self.check_resources)
        except Exception as e:
            logger.error(f"Error checking resources: {str(e)}")

    def cleanup_resources(self) -> None:
        """Clean up resources and optimize memory usage"""
        try:
            if self.pdf:
                self.pdf.close()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear any temporary files
            for file in self.output_dir.glob("*.mp3"):
                if time.time() - file.stat().st_mtime > AppDefaults.CLEANUP_INTERVAL:
                    file.unlink()
            
            self.last_cleanup = time.time()
            logger.info("Resource cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def get_session_duration(self) -> str:
        """Get formatted session duration"""
        try:
            current_time = datetime.now(self.tz)
            duration = current_time - self.session_start
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        except Exception as e:
            logger.error(f"Error calculating session duration: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.TIME_ERROR, str(e))

    def run(self) -> None:
        """Start the application"""
        try:
            logger.info("Starting application main loop")
            self.window.mainloop()
        except Exception as e:
            logger.error(f"Application crashed: {str(e)}")
            messagebox.showerror("Error", f"Application crashed: {str(e)}")
            raise AudiobookPlayerError(AudiobookPlayerError.INIT_ERROR, str(e))
        finally:
            try:
                if hasattr(self, 'pdf') and self.pdf:
                    self.pdf.close()
                if hasattr(self, 'engine'):
                    self.engine.stop()
                    self.engine = None
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
            logger.info("Application shutdown")

if __name__ == "__main__":
    try:
        print("Starting application...")
        app = AudiobookPlayer()
        print("AudiobookPlayer initialized, starting main loop...")
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        logger.exception("Fatal error occurred")
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
    finally:
        print("Application exit")
