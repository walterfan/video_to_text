# Text Extractor

A comprehensive web application for extracting text from various media sources including videos, audio files, and images. The application provides automatic speech recognition (ASR), translation capabilities, and optical character recognition (OCR) through an intuitive web interface.

## Features

### 🎥 Video & Audio Processing
- **Speech Recognition**: Convert video and audio files to text using OpenAI Whisper
- **Multi-format Support**: Supports MP4, AVI, MOV, MKV, MP3, WAV, OGG, M4A, AAC, FLAC
- **Real-time Processing**: Background processing with live status updates
- **Media Playback**: Built-in video and audio players for processed files

### 🌐 Translation
- **LLM Integration**: Advanced translation using ChatGPT-compatible APIs
- **Google Translate Fallback**: Reliable fallback translation service
- **Multi-language Support**: English, Chinese (Simplified/Traditional), Japanese, Korean, Spanish, French, German
- **Side-by-side Display**: View original and translated captions simultaneously

### 📷 OCR (Optical Character Recognition)
- **Image Text Extraction**: Extract text from images using Tesseract OCR
- **URL Detection**: Automatically detect and extract URLs from images
- **Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, TIFF
- **Copy to Clipboard**: Easy text copying functionality

### 🔐 User Authentication
- **Secure Login**: User authentication with Flask-Login
- **Registration**: User registration with email validation
- **Session Management**: Persistent user sessions
- **Protected Routes**: All features require user authentication

### 🌍 Internationalization
- **Multi-language UI**: English and Chinese interface support
- **Language Switching**: Dynamic language switching without page reload
- **Localized Content**: All text content is translatable

## Prerequisites

Please install the required dependencies:

```bash
# Install FFmpeg for media processing
brew install ffmpeg

# Install Tesseract for OCR
brew install tesseract

# Install Poetry for dependency management
curl -sSL https://install.python-poetry.org | python3 -

# Install Python dependencies
poetry install
```

## Quick Start

### 1. Environment Setup

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
ADMIN_EMAIL=admin@example.com

# LLM Configuration for Translation (optional)
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 2. Database Initialization

Initialize the database and create an admin user:

```bash
poetry run python init_db.py
```

### 3. Start the Application

Launch the web application:

```bash
./start.sh
```

The application will be available at `http://127.0.0.1:8000`

## Usage

### Web Interface

1. **Login**: Use the admin credentials created during database initialization
2. **Upload Media**: Upload video, audio, or image files through the web interface
3. **Configure Settings**: Choose Whisper model, source/target languages, and translation method
4. **Process**: Monitor real-time processing status
5. **View Results**: Download captions, view translations, and play media files

### Command Line Interface

For batch processing, you can still use the original command-line script:

```bash
poetry run python video_to_text.py -i ./example/5_minutes_for_50_years.mp4
```

## Configuration

### Whisper Models
- **tiny**: Fastest, least accurate
- **base**: Good balance of speed and accuracy
- **small**: Better accuracy, slower processing
- **medium**: High accuracy, slower processing
- **large**: Best accuracy, slowest processing

### Supported Languages
- **Source Languages**: Auto-detect, English, Chinese, Japanese, Korean, Spanish, French, German
- **Target Languages**: English, Chinese (Simplified/Traditional), Japanese, Korean, Spanish, French, German

### Translation Methods
- **LLM Translation**: Uses configured ChatGPT-compatible API
- **Google Translate**: Fallback translation service

## File Structure

```
video_to_text/
├── app/                    # Flask application
│   ├── templates/         # HTML templates
│   ├── static/           # Static files (CSS, JS, uploads)
│   ├── __init__.py       # App factory
│   ├── config.py         # Configuration settings
│   ├── forms.py          # Web forms
│   ├── models.py         # Database models
│   ├── views.py          # Route handlers
│   ├── video_processor.py # Media processing logic
│   ├── simple_llm_agent.py # LLM integration
│   └── ocr.py            # OCR functionality
├── translations/         # Internationalization files
├── example/             # Sample media files
├── init_db.py          # Database initialization
├── start.sh            # Application startup script
├── video_to_text.py    # Command-line interface
├── pyproject.toml      # Poetry dependencies
└── README.md           # This file
```

## Development

### Adding New Features

1. **Routes**: Add new routes in `app/views.py`
2. **Forms**: Define forms in `app/forms.py`
3. **Templates**: Create HTML templates in `app/templates/`
4. **Translations**: Update translation files in `translations/`

### Database Management

```bash
# Initialize database
poetry run python init_db.py

# Create new migration (if using Flask-Migrate)
flask db migrate -m "Description"

# Apply migrations
flask db upgrade
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is installed and in PATH
2. **Tesseract not found**: Install Tesseract OCR engine
3. **Permission errors**: Check file permissions for upload directory
4. **Memory issues**: Use smaller Whisper models for large files
5. **Translation errors**: Check LLM API configuration

### Logs

Application logs are available in the terminal when running in development mode. For production, configure proper logging in `app/config.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for optical character recognition
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Poetry](https://python-poetry.org/) for dependency management
