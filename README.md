# PDF to Audiobook Converter

A Tkinter-based application that converts PDF files to audiobooks with playback controls.

## Features

- Convert PDF files to audio
- Playback controls (play, pause, stop)
- Speed control
- Volume control
- Progress tracking
- Memory optimization
- Session time tracking

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.template` to `.env` and configure your settings:
   ```bash
   cp .env.template .env
   ```
   
Note: The application will automatically create the required `audiobook_output` and `pdf_books` directories on startup.

## Security Notes

- Never commit the `.env` file
- Keep your PDF files in the `pdf_books` directory
- Audio outputs are stored in `audiobook_output`
- Logs are stored in the configured log file
- All paths are relative to the application directory
- No sensitive information is stored in the code

## Security Best Practices

1. **Environment Variables**:
   - Always use `.env` for configuration
   - Never commit `.env` to version control
   - Use `.env.template` as a reference

2. **File Security**:
   - Only process PDFs you trust
   - Regularly clean up output directories
   - Don't store sensitive documents in project directories

3. **Dependencies**:
   - Keep dependencies updated
   - Review security advisories
   - Use specified versions in requirements.txt

For more details, see [SECURITY.md](SECURITY.md)

## Usage

1. Place your PDF files in the `pdf_books` directory
2. Run the application:
   ```bash
   python app.py
   ```
3. Select a PDF file and enjoy your audiobook!

## Environment Variables

Configure these in your `.env` file:

- `APP_NAME`: Application display name
- `OUTPUT_DIR`: Directory for audio outputs
- `PDF_BOOKS_DIR`: Directory for PDF files
- `TIMEZONE`: Your timezone
- `MAX_MEMORY_PERCENT`: Memory usage threshold
- `CLEANUP_INTERVAL`: Cleanup interval in seconds
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `LOG_FILE`: Log file location

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details
