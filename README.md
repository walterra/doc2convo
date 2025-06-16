# Conversation to Audio Converter

This project converts markdown-formatted conversations into audio podcasts with distinct voices for each speaker. It includes tools to generate conversations from web content and convert them to audio.

## Setup

### Setting up a Virtual Environment (Recommended for macOS)

It's recommended to use a virtual environment to avoid conflicts with system Python packages.

```bash
# Create a virtual environment
python3 -m venv convo-env

# Activate the virtual environment
source convo-env/bin/activate

# When you're done, deactivate with:
# deactivate
```

### Option 1: Using pyttsx3 (Simple, works offline)

```bash
# Make sure your virtual environment is activated first
pip install -r requirements.txt
python text_to_speech.py
```

### Option 2: Using edge-tts (Better quality voices)

```bash
# Make sure your virtual environment is activated first
pip install -r requirements-edge.txt
python edge_tts_converter.py
```

### Option 3: Full workflow with web content (Recommended)

```bash
# Make sure your virtual environment is activated first
pip install -r requirements-claude.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Complete Workflow: Web to Audio

The project includes `url2convo.py` which fetches web content and generates conversational podcasts using Claude AI.

### Quick Start (URL to MP3 in one command)

```bash
# Direct piping from URL to audio
python3 url2convo.py https://walterra.dev | python3 edge_tts_converter.py - -o walterra-dev.mp3

# With custom style/personality
python3 url2convo.py https://walterra.dev -s "Make it humorous with tech jokes" | python3 edge_tts_converter.py -
```

### Step-by-Step Usage

1. **Generate conversation from URL**

   ```bash
   # Output to file
   python3 url2convo.py https://walterra.dev -o WALTERRA-DEV-CONVO.md

   # Output to stdout (for piping)
   python3 url2convo.py https://walterra.dev

   # With custom system prompt
   python3 url2convo.py https://walterra.dev -s "Make it humorous with tech jokes"
   ```

2. **Convert conversation to audio**

   ```bash
   # From file
   python3 edge_tts_converter.py WALTERRA-DEV-CONVO.md -o walterra-dev.mp3

   # From stdin
   cat WALTERRA-DEV-CONVO.md | python3 edge_tts_converter.py - -o walterra-dev.mp3

   # Interactive mode (prompts for file)
   python3 edge_tts_converter.py
   ```

## How it works

1. **url2convo.py**: Fetches web content, cleans HTML, and uses Claude to generate a natural conversation
2. **edge_tts_converter.py**: Parses conversation markdown (format: `**SPEAKER:** text`)
3. Each speaker is assigned a different voice (ALEX: male, JORDAN: female)
4. Audio is generated line by line with natural pauses
5. All segments are combined into a single MP3 file

## Voice Configuration

- **ALEX**: Male voice (Christopher in edge-tts)
- **JORDAN**: Female voice (Jenny in edge-tts)

## Output

The final podcast is saved as `podcast.mp3` or custom file name in the same directory.

## Requirements

- Python 3.7+
- For edge-tts: Internet connection (uses Microsoft Edge's text-to-speech service)
- For pyttsx3: Works offline using system TTS
- For url2convo: Anthropic API key (set as environment variable)

## Customization

### Voices

You can modify the voices in either script:

- In `edge_tts_converter.py`: Change the voice names in the `VOICES` dictionary
- In `text_to_speech.py`: Adjust rate and voice selection in `setup_voices()`

### Conversation Style

Use the `--system-prompt`/`-s` flag with url2convo.py to influence the conversation:

```bash
# Make it educational
python3 url2convo.py https://walterra.dev -s "Explain concepts like teaching to beginners"

# Add humor
python3 url2convo.py https://walterra.dev -s "Include tech jokes and puns"

# Focus on specific aspects
python3 url2convo.py https://walterra.dev -s "Focus on the technical implementation details"
```

## Examples

```bash
# Convert a blog post to podcast
python3 url2convo.py https://walterra.dev/blog/2025-05-16-html-to-image-rendering-server | python3 edge_tts_converter.py - -o node-html2img-render-server-podcast.mp3

# Create a funny tech news summary
python3 url2convo.py https://techcrunch.com/2025/06/04/elon-musks-introduction-to-politics/ -s "Make it a roasting comedy show" -o ROAST-CONVO.md
python3 edge_tts_converter.py ROAST-CONVO.md
```
