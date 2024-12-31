"""
PDF to Audiobook Application
"""
import os
import sys
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from audio_engine import AudioEngine
from pdf_processor import PDFProcessor
from errors import UIError, ERROR_CODES

logger = logging.getLogger(__name__)

class AppDefaults:
    """Application default values"""
    WINDOW_TITLE = "PDF to Audiobook"
    WINDOW_MIN_WIDTH = 400
    WINDOW_MIN_HEIGHT = 600
    WINDOW_PADDING = 20
    INITIAL_PAGE = 1
    READING_SPEED = 200
    INITIAL_VOLUME = 100

class PDFAudiobookApp:
    def __init__(self):
        """Initialize the application"""
        self.window = tk.Tk()
        self.setup_window()
        
        # Initialize components
        self.audio_engine = AudioEngine()
        self.pdf_processor = None
        
        # Control flags
        self.is_reading = False
        self.stop_event = threading.Event()
        
        # Create widgets
        self.create_widgets()
        
        # Update window size to fit content
        self.window.update_idletasks()
        width = max(self.window.winfo_reqwidth() + AppDefaults.WINDOW_PADDING,
                   AppDefaults.WINDOW_MIN_WIDTH)
        height = max(self.window.winfo_reqheight() + AppDefaults.WINDOW_PADDING,
                    AppDefaults.WINDOW_MIN_HEIGHT)
        self.window.geometry(f"{width}x{height}")
        
    def setup_window(self) -> None:
        """Set up the main window"""
        self.window.title(AppDefaults.WINDOW_TITLE)
        self.window.minsize(AppDefaults.WINDOW_MIN_WIDTH, AppDefaults.WINDOW_MIN_HEIGHT)
        
        # Configure grid weights for resizing
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
    def create_widgets(self) -> None:
        """Create all GUI widgets"""
        # Main container with padding
        main_container = ttk.Frame(self.window, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure main container grid
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create all widget sections with proper spacing
        self.create_file_section(main_container)
        self.create_voice_controls(main_container)
        self.create_page_controls(main_container)
        self.create_speed_controls(main_container)
        self.create_volume_controls(main_container)
        self.create_buttons()
        self.create_progress_section()
        
    def create_file_section(self, container: tk.Frame) -> None:
        """Create file selection widgets"""
        file_frame = ttk.LabelFrame(container, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        # File path display
        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = ttk.Label(file_frame, textvariable=self.file_path_var)
        file_path_label.pack(fill=tk.X, padx=5, pady=5)
        
    def create_voice_controls(self, container: tk.Frame) -> None:
        """Create voice selection widgets"""
        voice_frame = ttk.LabelFrame(container, text="Voice Selection", padding="10")
        voice_frame.pack(fill=tk.X, pady=5)
        
        # Get available voices
        voices = self.audio_engine.get_available_voices()
        
        # Voice selection combobox
        self.voice_var = tk.StringVar()
        voice_combo = ttk.Combobox(
            voice_frame, 
            textvariable=self.voice_var,
            state='readonly'
        )
        
        # Format voice names for display
        voice_options = []
        self.voice_ids = {}  # Map display names to voice IDs
        
        for voice in voices:
            name = voice['name']
            gender = voice['gender']
            display_name = f"{name} ({gender})"
            voice_options.append(display_name)
            self.voice_ids[display_name] = voice['id']
            
        voice_combo['values'] = voice_options
        
        # Select first voice by default
        if voice_options:
            voice_combo.set(voice_options[0])
            self.audio_engine.set_voice(self.voice_ids[voice_options[0]])
            
        # Update voice when selection changes
        voice_combo.bind('<<ComboboxSelected>>', 
                        lambda e: self.audio_engine.set_voice(
                            self.voice_ids[self.voice_var.get()]
                        ))
        
        voice_combo.pack(fill=tk.X, padx=5, pady=5)
        
    def create_page_controls(self, container: tk.Frame) -> None:
        """Create page control widgets"""
        page_frame = ttk.LabelFrame(container, text="Page Control", padding="10")
        page_frame.pack(fill=tk.X, pady=5)
        
        # Start page entry
        start_page_frame = ttk.Frame(page_frame)
        start_page_frame.pack(fill=tk.X)
        
        start_page_label = ttk.Label(start_page_frame, text="Start Page:")
        start_page_label.pack(side=tk.LEFT)
        
        self.start_page_entry = ttk.Entry(start_page_frame, width=10)
        self.start_page_entry.pack(side=tk.LEFT, padx=5)
        self.start_page_entry.insert(0, str(AppDefaults.INITIAL_PAGE))
        
    def create_speed_controls(self, container: tk.Frame) -> None:
        """Create speed control widgets"""
        speed_frame = ttk.LabelFrame(container, text="Reading Speed", padding="10")
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.reading_speed = tk.IntVar(value=AppDefaults.READING_SPEED)
        speed_scale = ttk.Scale(
            speed_frame,
            from_=100,
            to=500,
            variable=self.reading_speed,
            orient=tk.HORIZONTAL,
            command=lambda _: self.audio_engine.set_rate(self.reading_speed.get())
        )
        speed_scale.pack(fill=tk.X, padx=5, pady=5)
        
    def create_volume_controls(self, container: tk.Frame) -> None:
        """Create volume control widgets"""
        volume_frame = ttk.LabelFrame(container, text="Volume", padding="10")
        volume_frame.pack(fill=tk.X, pady=5)
        
        self.volume = tk.IntVar(value=AppDefaults.INITIAL_VOLUME)
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            variable=self.volume,
            orient=tk.HORIZONTAL,
            command=lambda _: self.audio_engine.set_volume(self.volume.get())
        )
        volume_scale.pack(fill=tk.X, padx=5, pady=5)
        
    def create_buttons(self) -> None:
        """Create control buttons"""
        # Button frame with padding
        button_frame = ttk.Frame(self.window, padding="10")
        button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Select PDF button
        self.select_button = tk.Button(
            button_frame,
            text="Select PDF",
            command=lambda: self.safe_call(self.select_pdf)
        )
        self.select_button.pack(fill=tk.X, pady=2)
        
        # Play button
        self.play_button = tk.Button(
            button_frame,
            text="Play",
            command=lambda: self.safe_call(self.start_audiobook)
        )
        self.play_button.pack(fill=tk.X, pady=2)
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=lambda: self.safe_call(self.stop_audiobook)
        )
        self.stop_button.pack(fill=tk.X, pady=2)
        
    def create_progress_section(self) -> None:
        """Create progress tracking widgets"""
        progress_frame = ttk.LabelFrame(self.window, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
    def safe_call(self, func: callable) -> None:
        """Safely execute a function and handle any errors"""
        try:
            return func()
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def select_pdf(self) -> None:
        """Open file dialog to select a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                # Close existing PDF if any
                if self.pdf_processor:
                    self.pdf_processor.close()
                    
                self.pdf_processor = PDFProcessor(file_path)
                self.file_path_var.set(os.path.basename(file_path))
                self.start_page_entry.delete(0, tk.END)
                self.start_page_entry.insert(0, str(AppDefaults.INITIAL_PAGE))
                self._reset_progress()
            except Exception as e:
                logger.error(f"Failed to load PDF: {str(e)}")
                messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
                
    def stop_audiobook(self) -> None:
        """Stop reading the audiobook"""
        self.is_reading = False
        self.stop_event.set()
        self.window.after(0, self._reset_state)  # Ensure proper cleanup
        
    def start_audiobook(self) -> None:
        """Start reading the audiobook"""
        if not self.pdf_processor or not self.pdf_processor.current_pdf:
            messagebox.showwarning("Warning", "Please select a PDF file first")
            return
            
        try:
            # Get the page number and validate
            current_page = int(self.start_page_entry.get())
            total_pages = self.pdf_processor.get_total_pages()
            
            if not 1 <= current_page <= total_pages:
                raise UIError(ERROR_CODES['INVALID_PAGE_NUMBER'], 
                            f"Page number must be between 1 and {total_pages}")
                
            # Set initial speed and volume
            self.audio_engine.set_rate(self.reading_speed.get())
            self.audio_engine.set_volume(self.volume.get())
            
            self.is_reading = True
            self.stop_event.clear()
            
            # Start reading in a separate thread
            thread = threading.Thread(
                target=self._read_pages,
                args=(current_page, total_pages),
                daemon=True
            )
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid page number. Please enter a valid number.")
            self._reset_state()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._reset_state()
            
    def _read_pages(self, start_page: int, total_pages: int) -> None:
        """Read pages in a separate thread"""
        try:
            current_page = start_page
            
            # Continue reading until stopped or reached end
            while current_page <= total_pages and self.is_reading and not self.stop_event.is_set():
                # Extract text from the current page
                text = self.pdf_processor.extract_text(current_page - 1)
                
                if text and text != "Page is empty or contains no readable text.":
                    # Split into sentences and read them
                    sentences = [s.strip() for s in text.split('.') if s.strip()]
                    total_sentences = len(sentences)
                    
                    for i, sentence in enumerate(sentences, 1):
                        if not self.is_reading or self.stop_event.is_set():
                            return
                            
                        self.audio_engine.speak(sentence + '.')
                        
                        # Update progress
                        progress = (i / total_sentences) * 100
                        self.window.after(0, self._update_progress, progress)
                        
                    # Move to next page
                    current_page += 1
                    # Update page number and reset progress
                    self.window.after(0, self._update_page, current_page)
                else:
                    # Skip empty page
                    current_page += 1
                    self.window.after(0, self._update_page, current_page)
                    
            if current_page > total_pages and self.is_reading:
                self.audio_engine.speak("End of document reached")
            
        except Exception as e:
            logger.error(f"Error reading pages: {str(e)}")
            self.window.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.window.after(0, self._reset_state)
            
    def _update_progress(self, progress: float) -> None:
        """Update progress bar in GUI thread"""
        if self.is_reading:  # Only update if still reading
            self.progress_var.set(progress)
        
    def _update_page(self, page: int) -> None:
        """Update page number in GUI thread"""
        self.start_page_entry.delete(0, tk.END)
        self.start_page_entry.insert(0, str(page))
        self.progress_var.set(0)  # Reset progress for new page
        
    def _reset_state(self) -> None:
        """Reset the reading state"""
        self.is_reading = False
        self.stop_event.clear()
        if self.window and self.window.winfo_exists():
            self.play_button.config(text="Play")  # Only update if window exists
            
    def _reset_progress(self) -> None:
        """Reset progress indicators"""
        if self.window and self.window.winfo_exists():
            self.progress_var.set(0)
            self.play_button.config(text="Play")
            
    def reset_application(self) -> None:
        """Reset the application to its initial state"""
        try:
            # Stop any ongoing reading
            self.stop_audiobook()
            
            # Only update GUI if window exists
            if self.window and self.window.winfo_exists():
                # Reset GUI elements
                self.file_path_var.set("No file selected")
                self.start_page_entry.delete(0, tk.END)
                self.start_page_entry.insert(0, str(AppDefaults.INITIAL_PAGE))
                self.reading_speed.set(AppDefaults.READING_SPEED)
                self.volume.set(AppDefaults.INITIAL_VOLUME)
                self._reset_progress()
            
            # Reset PDF processor
            if self.pdf_processor:
                self.pdf_processor.close()
            self.pdf_processor = None
            
            # Reset audio engine settings
            self.audio_engine.set_rate(AppDefaults.READING_SPEED)
            self.audio_engine.set_volume(AppDefaults.INITIAL_VOLUME)
            self.audio_engine.cleanup()  # Clean up audio engine resources
            
        except Exception as e:
            logger.error(f"Error resetting application: {str(e)}")
            if self.window and self.window.winfo_exists():
                messagebox.showerror("Error", f"Failed to reset application: {str(e)}")
            
    def run(self) -> None:
        """Start the application"""
        try:
            # Set up window close handler
            self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.window.mainloop()
        except Exception as e:
            logger.error(f"Error running application: {str(e)}")
        finally:
            self._cleanup()
            
    def _on_closing(self) -> None:
        """Handle window closing event"""
        try:
            self._cleanup()
            self.window.destroy()
        except Exception as e:
            logger.error(f"Error during window closing: {str(e)}")
            
    def _cleanup(self) -> None:
        """Clean up all resources"""
        try:
            # Stop any ongoing reading
            self.stop_audiobook()
            
            # Clean up resources
            if self.pdf_processor:
                self.pdf_processor.close()
            if hasattr(self, 'audio_engine'):
                self.audio_engine.cleanup()
        except Exception as e:
            logger.error(f"Error during final cleanup: {str(e)}")
                
if __name__ == "__main__":
    app = PDFAudiobookApp()
    app.run()
