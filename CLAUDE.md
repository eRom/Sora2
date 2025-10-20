# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python video generation project that uses OpenAI's Sora2 API to create videos from text prompts. The project is written in French and provides a simple command-line interface for generating videos asynchronously with the Sora2 API.

## Key Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API configuration (copy the example file)
cp .env.example .env
# Edit .env with your actual API key
```

### Running the Application
```bash
# Generate a video from prompt.md
python3 generate.py

# Generate a video with reference image
python3 generate.py --reference-image input_reference/my_image.jpg
python3 generate.py -r input_reference/my_image.jpg

# Note: The README mentions generate_video.py but the actual file is generate.py
```

### File Structure
```
.
├── .env.example          # Template for API configuration
├── .env                  # Actual API configuration (gitignored)
├── prompt.md             # Video generation prompt (edit this file)
├── generate.py           # Main generation script
├── requirements.txt      # Python dependencies
├── input_reference/      # Directory for reference images
├── metadata/            # JSON metadata for generated videos
└── output/              # Generated MP4 video files
```

## Architecture Overview

The codebase consists of a single main script (`generate.py`) with the following key components:

### Core Functions
- `generate_video()` - Handles API communication with OpenAI's video generation endpoint
- `wait_for_completion()` - Polls for async video generation completion with progress tracking
- `download_video_from_api()` - Downloads completed videos with integrity checking and progress display
- `read_prompt()` - Reads and parses the video description from `prompt.md`
- `read_reference_image()` - Loads and validates reference images, converts to base64

### Key Features
- **Asynchronous Processing**: Videos are generated asynchronously with status polling
- **Reference Image Support**: Optional image reference with dimension validation and path restrictions
- **Error Handling**: Comprehensive error handling including moderation policy detection
- **Retry Logic**: Built-in retry mechanism for network failures with exponential backoff
- **Progress Tracking**: Real-time progress display for both generation and download phases
- **Metadata Management**: JSON metadata storage for tracking video generation history
- **File Integrity**: SHA256 hashing for downloaded file verification

### Configuration Management
The project uses environment variables loaded from `.env`:
- `SORA_API_KEY`: OpenAI API key for video generation
- `SORA_MODEL`: Model version (`sora-2` or `sora-2-pro`)
- `SORA_DURATION`: Video duration in seconds (4, 8, or 12)
- `SORA_SIZE`: Video resolution (e.g., `1280x720`)
- `SORA_REFERENCE_IMAGE`: Optional path to reference image in `input_reference/` directory

### Reference Image Validation
Reference images must:
- Be located in the `input_reference/` directory (security restriction)
- Match the exact dimensions specified in `SORA_SIZE`
- Be in supported formats: JPG/JPEG, PNG, GIF, BMP, WebP
- Have proper dimensions validated using PIL/Pillow library

### Error Handling and Moderation
The script includes sophisticated error handling:
- Pre-generation moderation detection to avoid billing for rejected content
- Post-generation moderation with support contact suggestions
- Network retry logic with exponential backoff
- Comprehensive metadata logging for debugging

### API Integration
Uses OpenAI's video generation API at `https://api.openai.com/v1/videos` with:
- RESTful API calls using the `requests` library
- Bearer token authentication
- Async video generation workflow
- Direct download URLs for completed videos
- Support for reference image input via base64 encoding
- Optional `input` parameter for reference images in API payload

## Development Notes

- The script is designed as a single-file application for simplicity
- All output files include timestamps and video IDs for uniqueness
- Metadata files track the complete generation lifecycle for debugging
- The code includes French language comments and user messages
- Error messages provide actionable feedback and recovery suggestions
- Reference images are restricted to `input_reference/` directory for security
- Dimension validation prevents API failures due to mismatched image sizes
- The script uses `argparse` for professional command-line interface
- PIL/Pillow is required for image dimension validation