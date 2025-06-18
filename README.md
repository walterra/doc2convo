# doc2convo

This project converts markdown-formatted conversations into audio podcasts with distinct voices for each speaker. It includes tools to generate conversations from web content and convert them to audio.

https://github.com/user-attachments/assets/3d7ba715-2756-4003-9ccf-ad9d9b791353

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
pip install -e .

# For development tools (optional)
pip install -e ".[dev]"

# Set your Anthropic API key (for doc2md-convo command)
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

The project includes the `doc2md-convo` command which fetches web content or processes local files and generates conversational podcasts using Claude AI.

### Supported Input Types

- **URLs**: Any web page (HTML content is cleaned and processed)
- **Text files**: `.txt` files with plain text content
- **Markdown files**: `.md` files with markdown formatting
- **PDF files**: `.pdf` files (requires PyPDF2 - included in requirements)

### Quick Start Examples

```bash
# Direct piping from URL to audio
doc2md-convo https://walterra.dev | md-convo2mp3 - -o walterra-dev.mp3

# From local text file
doc2md-convo document.txt | md-convo2mp3 - -o document-podcast.mp3

# From local text file with Orpheus TTS (optimized prompt)
doc2md-convo document.txt --tts-engine orpheus | md-convo2mp3 - --tts-engine orpheus -o document-podcast.mp3

# From PDF file
doc2md-convo report.pdf | md-convo2mp3 - -o report-podcast.mp3

# With custom style/personality
doc2md-convo document.md -s "Make it humorous with tech jokes" | md-convo2mp3 -

# Using Orpheus TTS with custom voices (optimized prompt)
doc2md-convo article.md --tts-engine orpheus | md-convo2mp3 - --tts-engine orpheus --alex-voice zac --jordan-voice zoe
```

### Step-by-Step Usage

1. **Generate conversation from URL or local file**

   ```bash
   # From URL - output to file
   doc2md-convo https://walterra.dev -o WALTERRA-DEV-CONVO.md

   # From local text file
   doc2md-convo document.txt -o DOCUMENT-CONVO.md

   # From markdown file
   doc2md-convo README.md -o README-CONVO.md

   # From PDF file
   doc2md-convo report.pdf -o REPORT-CONVO.md

   # Output to stdout (for piping)
   doc2md-convo document.txt

   # With custom system prompt
   doc2md-convo document.md -s "Make it humorous with tech jokes"

   # Using Orpheus TTS (generates conversation with emotional tags and shorter segments)
   doc2md-convo document.md --tts-engine orpheus -o DOCUMENT-CONVO.md
   ```

2. **Convert conversation to audio**

   ```bash
   # From file
   md-convo2mp3 WALTERRA-DEV-CONVO.md -o walterra-dev.mp3

   # From stdin
   cat WALTERRA-DEV-CONVO.md | md-convo2mp3 - -o walterra-dev.mp3

   # Interactive mode (prompts for file)
   md-convo2mp3

   # Using Orpheus TTS instead of edge-tts
   md-convo2mp3 DOCUMENT-CONVO.md --tts-engine orpheus

   # Custom voices with Orpheus TTS
   md-convo2mp3 DOCUMENT-CONVO.md --tts-engine orpheus --alex-voice zac --jordan-voice zoe

   # See help for options
   md-convo2mp3 --help
   ```

## How it works

1. **doc2md-convo**:
   - For URLs: Fetches web content, cleans HTML, and uses Claude to generate a natural conversation
   - For local files: Reads content from .txt, .md, or .pdf files and processes with Claude
2. **md-convo2mp3**: Parses conversation markdown (format: `**SPEAKER:** text`)
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
- **⚠️ IMPORTANT**: Use `--tts-engine orpheus` with `doc2md-convo` to generate conversations optimized for Orpheus TTS (shorter dialogue segments and emotional tags)

## Output

The final podcast is saved as `podcast.mp3` or custom file name in the same directory.

## Requirements

- Python 3.7+
- For `doc2md-convo.py`: Anthropic API key (set as environment variable)
- For `md-convo2mp3.py` with Edge TTS: Internet connection (uses Microsoft Edge's text-to-speech service)
- For `md-convo2mp3.py` with Orpheus TTS:
  - **⚠️ IMPORTANT**: At least 2.5GB of RAM for the model
  - LM Studio running with orpheus-3b-0.1-ft model (Q4_K_M quant) at model path: isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF
  - API server enabled at http://127.0.0.1:1234

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

Use the `--system-prompt`/`-s` flag with doc2md-convo to influence the conversation:

```bash
# Make it educational
doc2md-convo https://walterra.dev -s "Explain concepts like teaching to beginners"

# Add humor
doc2md-convo https://walterra.dev -s "Include tech jokes and puns"

# Focus on specific aspects
doc2md-convo https://walterra.dev -s "Focus on the technical implementation details"
```

## Examples

```bash
# Convert a blog post to podcast
doc2md-convo https://walterra.dev/blog/2025-05-16-html-to-image-rendering-server | md-convo2mp3 - -o node-html2img-render-server-podcast.mp3

# Convert local documentation to podcast
doc2md-convo README.md | md-convo2mp3 - -o readme-podcast.mp3

# Process a research paper PDF
doc2md-convo research-paper.pdf -s "Explain like teaching to graduate students" -o RESEARCH-CONVO.md
md-convo2mp3 RESEARCH-CONVO.md -o research-podcast.mp3

# Create a funny tech news summary from URL
doc2md-convo https://techcrunch.com/2025/06/04/elon-musks-introduction-to-politics/ -s "Make it a roasting comedy show" -o ROAST-CONVO.md
md-convo2mp3 ROAST-CONVO.md

# Using Orpheus TTS with optimized conversation generation
doc2md-convo research-paper.pdf --tts-engine orpheus -s "Include emotional reactions" -o RESEARCH-ORPHEUS-CONVO.md
md-convo2mp3 RESEARCH-ORPHEUS-CONVO.md --tts-engine orpheus --alex-voice zac --jordan-voice tara
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
