# doc2convo

This project converts markdown-formatted conversations into audio podcasts with distinct voices for each speaker. It includes tools to generate conversations from web content and convert them to audio.

## Setup

### Setting up a Virtual Environment (Recommended for macOS)

It's recommended to use a virtual environment to avoid conflicts with system Python packages.

```bash
# Create a virtual environment
python3 -m venv convo-env

# Activate the virtual environment
source ./convo-env/bin/activate

# When you're done, deactivate with:
deactivate
```

### Installation

```bash
# Make sure your virtual environment is activated first
pip install -r requirements.txt

# For development tools (optional)
pip install -r requirements-dev.txt

# Set your Anthropic API key (for url2convo.py)
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Complete Workflow: Web to Audio

The project includes `url2convo.py` which fetches web content or processes local files and generates conversational podcasts using Claude AI.

### Supported Input Types

- **URLs**: Any web page (HTML content is cleaned and processed)
- **Text files**: `.txt` files with plain text content
- **Markdown files**: `.md` files with markdown formatting
- **PDF files**: `.pdf` files (requires PyPDF2 - included in requirements)

### Quick Start Examples

```bash
# Direct piping from URL to audio
python3 url2convo.py https://walterra.dev | python3 edge_tts_converter.py - -o walterra-dev.mp3

# From local text file
python3 url2convo.py document.txt | python3 edge_tts_converter.py - -o document-podcast.mp3

# From PDF file
python3 url2convo.py report.pdf | python3 edge_tts_converter.py - -o report-podcast.mp3

# With custom style/personality
python3 url2convo.py document.md -s "Make it humorous with tech jokes" | python3 edge_tts_converter.py -
```

### Step-by-Step Usage

1. **Generate conversation from URL or local file**

   ```bash
   # From URL - output to file
   python3 url2convo.py https://walterra.dev -o WALTERRA-DEV-CONVO.md

   # From local text file
   python3 url2convo.py document.txt -o DOCUMENT-CONVO.md

   # From markdown file
   python3 url2convo.py README.md -o README-CONVO.md

   # From PDF file
   python3 url2convo.py report.pdf -o REPORT-CONVO.md

   # Output to stdout (for piping)
   python3 url2convo.py document.txt

   # With custom system prompt
   python3 url2convo.py document.md -s "Make it humorous with tech jokes"
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

1. **url2convo.py**:
   - For URLs: Fetches web content, cleans HTML, and uses Claude to generate a natural conversation
   - For local files: Reads content from .txt, .md, or .pdf files and processes with Claude
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
- For url2convo: Anthropic API key (set as environment variable)

## Customization

### Voices

You can modify the voices in `edge_tts_converter.py` by changing the voice names in the `VOICES` dictionary.

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

# Convert local documentation to podcast
python3 url2convo.py README.md | python3 edge_tts_converter.py - -o readme-podcast.mp3

# Process a research paper PDF
python3 url2convo.py research-paper.pdf -s "Explain like teaching to graduate students" -o RESEARCH-CONVO.md
python3 edge_tts_converter.py RESEARCH-CONVO.md -o research-podcast.mp3

# Create a funny tech news summary from URL
python3 url2convo.py https://techcrunch.com/2025/06/04/elon-musks-introduction-to-politics/ -s "Make it a roasting comedy show" -o ROAST-CONVO.md
python3 edge_tts_converter.py ROAST-CONVO.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
