# doc2convo

This project converts markdown-formatted conversations into audio podcasts with distinct voices for each speaker. It includes tools to generate conversations from web content and convert them to audio.

## Setup

### Setting up a Virtual Environment (Recommended for macOS)

It's recommended to use a virtual environment to avoid conflicts with system Python packages.

```bash
# Create a virtual environment
python3 -m venv doc2convo-env

# Activate the virtual environment
source ./doc2convo-env/bin/activate

# When you're done, deactivate with:
deactivate
```

### Installation

```bash
# Make sure your virtual environment is activated first
pip install -r requirements.txt

# For development tools (optional)
pip install -r requirements-dev.txt

# Set your Anthropic API key (for doc2md-convo.py)
export ANTHROPIC_API_KEY='your-api-key-here'

# For Orpheus TTS support (optional)
python3 setup-orpheus.py

# To use Orpheus TTS:
# 1. Run LM Studio with orpheus-3b-0.1-ft model (Q4_K_M quant)
#    Model path: isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF
# 2. Enable API server at http://127.0.0.1:1234
# 3. The tools will automatically import from the local orpheus-tts-local directory
# Note: This model requires about 2.5GB of RAM
```

## Complete Workflow: Web to Audio

The project includes `doc2md-convo.py` which fetches web content or processes local files and generates conversational podcasts using Claude AI.

### Supported Input Types

- **URLs**: Any web page (HTML content is cleaned and processed)
- **Text files**: `.txt` files with plain text content
- **Markdown files**: `.md` files with markdown formatting
- **PDF files**: `.pdf` files (requires PyPDF2 - included in requirements)

### Quick Start Examples

```bash
# Direct piping from URL to audio (using edge-tts)
python3 doc2md-convo.py https://walterra.dev | python3 md-convo2mp3.py - -o walterra-dev.mp3

# From local text file with Orpheus TTS
python3 doc2md-convo.py document.txt --tts-engine orpheus | python3 md-convo2mp3.py - --tts-engine orpheus -o document-podcast.mp3

# From PDF file
python3 doc2md-convo.py report.pdf | python3 md-convo2mp3.py - -o report-podcast.mp3

# With custom style/personality
python3 doc2md-convo.py document.md -s "Make it humorous with tech jokes" | python3 md-convo2mp3.py -

# Using Orpheus TTS with custom voices
python3 doc2md-convo.py article.md --tts-engine orpheus | python3 md-convo2mp3.py - --tts-engine orpheus --alex-voice zac --jordan-voice zoe
```

### Step-by-Step Usage

1. **Generate conversation from URL or local file**

   ```bash
   # From URL - output to file
   python3 doc2md-convo.py https://walterra.dev -o WALTERRA-DEV-CONVO.md

   # From local text file
   python3 doc2md-convo.py document.txt -o DOCUMENT-CONVO.md

   # From markdown file
   python3 doc2md-convo.py README.md -o README-CONVO.md

   # From PDF file
   python3 doc2md-convo.py report.pdf -o REPORT-CONVO.md

   # Output to stdout (for piping)
   python3 doc2md-convo.py document.txt

   # With custom system prompt
   python3 doc2md-convo.py document.md -s "Make it humorous with tech jokes"

   # Using Orpheus TTS (with emotional tags support)
   python3 doc2md-convo.py document.md --tts-engine orpheus -o DOCUMENT-CONVO.md
   ```

2. **Convert conversation to audio**

   ```bash
   # From file
   python3 md-convo2mp3.py WALTERRA-DEV-CONVO.md -o walterra-dev.mp3

   # From stdin
   cat WALTERRA-DEV-CONVO.md | python3 md-convo2mp3.py - -o walterra-dev.mp3

   # Interactive mode (prompts for file)
   python3 md-convo2mp3.py

   # Using Orpheus TTS instead of edge-tts
   python3 md-convo2mp3.py DOCUMENT-CONVO.md --tts-engine orpheus

   # Custom voices with Orpheus TTS
   python3 md-convo2mp3.py DOCUMENT-CONVO.md --tts-engine orpheus --alex-voice zac --jordan-voice zoe
   ```

## How it works

1. **doc2md-convo.py**:
   - For URLs: Fetches web content, cleans HTML, and uses Claude to generate a natural conversation
   - For local files: Reads content from .txt, .md, or .pdf files and processes with Claude
2. **md-convo2mp3.py**: Parses conversation markdown (format: `**SPEAKER:** text`)
3. Each speaker is assigned a different voice (ALEX: male, JORDAN: female)
4. Audio is generated line by line with natural pauses
5. All segments are combined into a single MP3 file

## Voice Configuration

### Edge TTS (Default)

- **ALEX**: Male voice (Christopher in edge-tts)
- **JORDAN**: Female voice (Jenny in edge-tts)

### Orpheus TTS

- **ALEX**: Default is 'leo' (male voice)
- **JORDAN**: Default is 'tara' (female voice)
- Available voices: tara, leah, jess, leo, dan, mia, zac, zoe
- Supports emotional tags: `<giggle>`, `<laugh>`, `<chuckle>`, `<sigh>`, `<cough>`, `<sniffle>`, `<groan>`, `<yawn>`, `<gasp>`

## Output

The final podcast is saved as `podcast.mp3` or custom file name in the same directory.

## Requirements

- Python 3.7+
- For `doc2md-convo.py`: Anthropic API key (set as environment variable)
- For `md-convo2mp3.py` with Edge TTS: Internet connection (uses Microsoft Edge's text-to-speech service)
- For `md-convo2mp3.py` with Orpheus TTS:
  - LM Studio running with orpheus-3b-0.1-ft model (Q4_K_M quant) at model path: isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF
  - API server enabled at http://127.0.0.1:1234
  - At least 2.5GB of RAM for the model

## Customization

### Voices

#### Edge TTS

You can modify the voices in `md-convo2mp3.py` by changing the voice names in the `EDGE_VOICES` dictionary.

#### Orpheus TTS

Specify custom voices using the command line arguments:

```bash
python3 md-convo2mp3.py conversation.md --tts-engine orpheus --alex-voice leo --jordan-voice tara
```

#### Emotional Tags (Orpheus TTS only)

When using Orpheus TTS, you can include emotional tags in the conversation:

```
**ALEX:** That's <laugh> really interesting! I never thought about it that way.
**JORDAN:** <sigh> I know, right? The implications are quite profound.
```

### Conversation Style

Use the `--system-prompt`/`-s` flag with doc2md-convo.py to influence the conversation:

```bash
# Make it educational
python3 doc2md-convo.py https://walterra.dev -s "Explain concepts like teaching to beginners"

# Add humor
python3 doc2md-convo.py https://walterra.dev -s "Include tech jokes and puns"

# Focus on specific aspects
python3 doc2md-convo.py https://walterra.dev -s "Focus on the technical implementation details"
```

## Examples

```bash
# Convert a blog post to podcast
python3 doc2md-convo.py https://walterra.dev/blog/2025-05-16-html-to-image-rendering-server | python3 md-convo2mp3.py - -o node-html2img-render-server-podcast.mp3

# Convert local documentation to podcast
python3 doc2md-convo.py README.md | python3 md-convo2mp3.py - -o readme-podcast.mp3

# Process a research paper PDF
python3 doc2md-convo.py research-paper.pdf -s "Explain like teaching to graduate students" -o RESEARCH-CONVO.md
python3 md-convo2mp3.py RESEARCH-CONVO.md -o research-podcast.mp3

# Create a funny tech news summary from URL
python3 doc2md-convo.py https://techcrunch.com/2025/06/04/elon-musks-introduction-to-politics/ -s "Make it a roasting comedy show" -o ROAST-CONVO.md
python3 md-convo2mp3.py ROAST-CONVO.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
