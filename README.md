# Conversation to Audio Converter

This project converts markdown-formatted conversations into audio podcasts with distinct voices for each speaker.

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

## How it works

1. The scripts parse `DAILY-CONVO.md` to extract speaker lines (format: `**SPEAKER:** text`)
2. Each speaker is assigned a different voice
3. The audio is generated line by line
4. All audio segments are combined into a single MP3 file

## Voice Configuration

- **ALEX**: Male voice (Christopher in edge-tts)
- **JORDAN**: Female voice (Jenny in edge-tts)

## Output

The final podcast is saved as `podcast.mp3` in the same directory.

## Requirements

- Python 3.7+
- For edge-tts: Internet connection (uses Microsoft Edge's text-to-speech service)
- For pyttsx3: Works offline using system TTS

## Customization

You can modify the voices in either script:
- In `edge_tts_converter.py`: Change the voice names in the `VOICES` dictionary
- In `text_to_speech.py`: Adjust rate and voice selection in `setup_voices()`