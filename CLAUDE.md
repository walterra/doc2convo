# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

doc2convo is a Python-based conversation-to-audio converter that transforms markdown-formatted conversations into audio podcasts with distinct voices for each speaker using Microsoft Edge's neural voices via `edge_tts_converter.py`.

## Development Commands

### Setup and Run
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
1. **Conversation Parser** (`parse_conversation()` in edge_tts_converter.py)
   - Regex pattern: `r'\*\*([A-Z]+):\*\* (.+)'`
   - Returns list of (speaker, text) tuples

2. **Voice Mapping**
   - ALEX: Male voice (Christopher in edge-tts)
   - JORDAN: Female voice (Jenny in edge-tts)

3. **Audio Processing**
   - Generates temporary MP3s, combines with 300ms pauses, outputs to `podcast.mp3`

### Key Implementation Details
- Input file hardcoded as `DAILY-CONVO.md`
- Output file hardcoded as `podcast.mp3`
- edge_tts_converter.py uses async/await pattern
- Temporary files cleaned up automatically

### Important Notes
- No error handling for missing files or TTS failures
- edge-tts requires internet connection
- Unknown speakers default to ALEX's voice