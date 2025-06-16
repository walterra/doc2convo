# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

doc2convo is a Python-based conversation-to-audio converter that transforms markdown-formatted conversations into audio podcasts with distinct voices for each speaker. The project provides two implementations:
- `text_to_speech.py` - Offline TTS using pyttsx3
- `edge_tts_converter.py` - Online TTS using Microsoft Edge's neural voices

## Development Commands

### Setup and Run (pyttsx3 version)
```bash
pip install -r requirements.txt
python text_to_speech.py
```

### Setup and Run (edge-tts version - recommended)
```bash
pip install -r requirements-edge.txt
python edge_tts_converter.py
```

### Testing Changes
Since there are no automated tests, manually verify:
1. Ensure `DAILY-CONVO.md` exists with proper format: `**SPEAKER:** text`
2. Run the script and check output
3. For edge-tts version, verify `podcast.mp3` is created

## Code Architecture

### Core Components
1. **Conversation Parser** (`parse_conversation()` in both files)
   - Regex pattern: `r'\*\*([A-Z]+):\*\* (.+)'`
   - Returns list of (speaker, text) tuples

2. **Voice Mapping**
   - ALEX: Male voice (Christopher in edge-tts, system male voice in pyttsx3)
   - JORDAN: Female voice (Jenny in edge-tts, system female voice in pyttsx3)

3. **Audio Processing**
   - pyttsx3: Direct playback, no file output
   - edge-tts: Generates temporary MP3s, combines with 300ms pauses, outputs to `podcast.mp3`

### Key Implementation Details
- Input file hardcoded as `DAILY-CONVO.md`
- Output file (edge-tts only) hardcoded as `podcast.mp3`
- edge_tts_converter.py uses async/await pattern
- Temporary files cleaned up automatically in edge-tts version

### Important Notes
- No error handling for missing files or TTS failures
- edge-tts requires internet connection
- pyttsx3 uses system TTS (quality varies by OS)
- Unknown speakers default to ALEX's voice