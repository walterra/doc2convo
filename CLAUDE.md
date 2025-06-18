# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

doc2convo is a Python tool that converts web content and documents into conversational audio podcasts. It consists of two main components:

- `doc2md-convo.py` - Fetches content from URLs or local files and generates natural conversations using Claude AI
- `md-convo2mp3.py` - Converts conversation markdown to audio using Microsoft Edge's neural voices

## Development Commands

### Setup Virtual Environment

```bash
python3 -m venv doc2convo-env
source ./doc2convo-env/bin/activate
```

### Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development tools (optional)
pip install -r requirements-dev.txt
```

### Code Quality Commands

```bash
# Format code
python scripts/format_python.py

# Check license headers
python scripts/check_license_header.py

# Add missing license headers
python scripts/add_license_header.py

# Run linting
flake8 .

# Type checking
mypy md-convo2mp3.py doc2md-convo.py
```

### Running the Tools

```bash
# Set API key for doc2md-convo
export ANTHROPIC_API_KEY='your-api-key-here'

# Generate conversation from URL/file
python3 doc2md-convo.py https://example.com -o OUTPUT-CONVO.md
python3 doc2md-convo.py document.pdf -s "Make it humorous"

# Convert to audio
python3 md-convo2mp3.py INPUT-CONVO.md -o output.mp3

# Direct piping workflow
python3 doc2md-convo.py URL | python3 md-convo2mp3.py - -o podcast.mp3
```

## Code Architecture

### Core Workflow

The project implements a pipeline: Content Source → AI Conversation → Neural TTS Audio

1. **Content Ingestion** (`doc2md-convo.py`)

   - Accepts URLs (via requests + BeautifulSoup for HTML cleaning)
   - Processes local files: .txt, .md, .pdf (via PyPDF2)
   - Uses Anthropic Claude to generate natural dialogues between ALEX and JORDAN
   - Supports custom system prompts to influence conversation style

2. **Audio Generation** (`md-convo2mp3.py`)
   - Parses markdown conversations (format: `**SPEAKER:** text`)
   - Maps speakers to voices: ALEX → ChristopherNeural, JORDAN → JennyNeural
   - Implements async TTS generation with edge-tts
   - Combines audio segments with 300ms pauses between turns
   - Supports both file input and stdin for piping

### Key Implementation Details

- All Python files must include MIT license header (enforced by scripts/)
- Code formatting: Black with 88-char line length + isort
- Conversation regex pattern: `r'\*\*([A-Z]+):\*\* (.+)'`
- Speech rate increased by 25% for natural flow
- Temporary audio files cleaned up automatically
- Output filenames auto-generated from source when using stdin

### Project Configuration

- `pyproject.toml` - Configures Black, isort, flake8, and mypy settings
- Development issues tracked in `dev/ISSUE-*.md` files
- No automated tests - manual verification required

### Git

- Use concise commit messages
- Do not add author information to commit messages
