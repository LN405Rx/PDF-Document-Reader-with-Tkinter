# PDF to Audiobook Converter

A simple GUI application that converts PDF files to audiobooks using text-to-speech technology. The application runs entirely locally on your system, requiring no internet connection or external services.

## Features

- Load and read PDF files
- Adjust reading speed and volume
- Select different TTS voices
- Navigate through pages
- Play/pause/stop functionality

## Local Processing

This application operates completely offline with all processing done locally:

1. **Text-to-Speech**:
   - Uses your system's built-in TTS engine (SAPI5 on Windows, espeak on Linux/macOS)
   - All voices are installed locally on your system
   - No internet connection required

2. **PDF Processing**:
   - Reads and extracts text from PDF files locally
   - No cloud services or external APIs needed
   - Works with files from your local system

3. **Data Privacy**:
   - All files remain on your computer
   - No data transmission to external services
   - Complete offline operation

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. For development and testing, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Use the GUI to:
   - Select a PDF file from your computer
   - Choose a voice from your system's installed voices
   - Adjust speed and volume
   - Start reading from any page
   - Control playback

## Project Structure

Core files:
- `app.py` - Main application and GUI using tkinter (built-in)
- `audio_engine.py` - Local text-to-speech functionality
- `pdf_processor.py` - Local PDF text extraction
- `errors.py` - Error handling

Required directories:
- `pdf_books/` - Store your PDF files here

## Dependencies

Core:
- pyttsx3 - Local text-to-speech engine interface
- pdfplumber - Local PDF text extraction
- typing-extensions - Type hints
- tkinter - Built-in GUI framework (comes with Python)

Development (optional):
- pytest - Testing framework
- memory-profiler - Performance optimization
- python-dotenv - Environment variables

## Performance

Since all processing is done locally:
- Fast operation with no network latency
- Reliable performance without internet dependency
- Resource usage limited only by your system's capabilities

## License

MIT License - See LICENSE file for details
