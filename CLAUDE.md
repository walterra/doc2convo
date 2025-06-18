# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

doc2convo is a Python package that converts web content and documents into conversational audio podcasts. It consists of two main components:

- `doc2md-convo` - Fetches content from URLs or local files and generates natural conversations using Claude AI
- `md-convo2mp3` - Converts conversation markdown to audio using Microsoft Edge's neural voices

## Development Commands

### Setup Virtual Environment

```bash
python3 -m venv doc2convo-env
source ./doc2convo-env/bin/activate
```

### Install Dependencies

```bash
# Install package in editable mode
pip install -e .

# For development tools
pip install -e ".[dev]"

# Or using requirements files (legacy)
pip install -r requirements.txt
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
mypy src/
```

### Running the Tools

```bash
# Set API key for doc2md-convo
export ANTHROPIC_API_KEY='your-api-key-here'

# Generate conversation from URL/file
doc2md-convo https://example.com -o OUTPUT-CONVO.md
doc2md-convo document.pdf -s "Make it humorous"

# Convert to audio (default: Edge TTS)
md-convo2mp3 INPUT-CONVO.md -o output.mp3

# Use Orpheus TTS (requires LM Studio running)
# First generate conversation optimized for Orpheus (shorter segments, emotional tags)
doc2md-convo document.pdf --tts-engine orpheus -o OUTPUT-CONVO.md
# Then convert to audio
md-convo2mp3 OUTPUT-CONVO.md --tts-engine orpheus -o output.mp3

# Direct piping workflow
doc2md-convo URL | md-convo2mp3 - -o podcast.mp3
```

## Code Architecture

### Core Workflow

The project implements a pipeline: Content Source → AI Conversation → Neural TTS Audio

1. **Content Ingestion** (`doc2md-convo`)

   - Accepts URLs (via requests + BeautifulSoup for HTML cleaning)
   - Processes local files: .txt, .md, .pdf (via PyPDF2)
   - Uses Anthropic Claude to generate natural dialogues between ALEX and JORDAN
   - Supports custom system prompts to influence conversation style

2. **Audio Generation** (`md-convo2mp3`)
   - Parses markdown conversations (format: `**SPEAKER:** text`)
   - Maps speakers to voices: ALEX → ChristopherNeural, JORDAN → JennyNeural
   - Implements async TTS generation with edge-tts
   - Combines audio segments with 300ms pauses between turns
   - Supports both file input and stdin for piping
   - **Orpheus TTS Support**: Optional local TTS via LM Studio; exits with error message if LM Studio is not available when selected

### Key Implementation Details

- All Python files must include MIT license header (enforced by scripts/)
- Code formatting: Black with 88-char line length + isort
- Conversation regex pattern: `r'\*\*([A-Z]+):\*\* (.+)'`
- Speech rate increased by 25% for natural flow
- Temporary audio files cleaned up automatically
- Output filenames auto-generated from source when using stdin

### Package Structure

The project is organized as a proper Python package:

```
src/doc2convo/
├── __init__.py          # Package initialization
├── cli/                 # Command-line interfaces
│   ├── main.py         # Main entry point
│   ├── doc2md.py       # Document to markdown CLI
│   └── md2mp3.py       # Markdown to audio CLI
├── converters/          # Audio conversion modules
│   └── audio.py        # AudioConverter class
├── generators/          # AI conversation generation
│   └── conversation.py # ConversationGenerator class
├── utils/               # Utility modules
│   └── content_fetcher.py # ContentFetcher class
└── exceptions.py        # Custom exceptions
```

### Project Configuration

- `pyproject.toml` - Package metadata and tool configurations (Black, isort, flake8, mypy)
- Development issues tracked in `dev/ISSUE-*.md` files
- No automated tests - manual verification required

## TTS Engine Options

### Edge TTS (Default)
- Uses Microsoft Edge neural voices (ChristopherNeural, JennyNeural)
- No setup required - works out of the box
- Requires internet connectivity

### Orpheus TTS (Local)
- Uses local neural TTS via LM Studio
- Requires setup: `python3 setup-orpheus.py`
- Requires LM Studio API server running at http://127.0.0.1:1234
- **Error Handling**: Script exits with clear error message if:
  - Orpheus TTS is not installed when `--tts-engine orpheus` is used
  - LM Studio API server is not running or unreachable
- Default voices: ALEX → leo (male), JORDAN → tara (female)

### Git

- Use concise commit messages
- Do not add author information to commit messages
