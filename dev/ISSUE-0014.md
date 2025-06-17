# Enhancement: Add ElevenLabs TTS Support

## Overview
Add support for ElevenLabs neural voices as an alternative to Microsoft Edge TTS in the `md-convo2mp3.py` component.

## Background
Currently, the project uses Microsoft Edge's neural voices (ChristopherNeural, JennyNeural) for text-to-speech conversion. ElevenLabs offers high-quality neural voices that could provide better audio quality and more voice options.

## Proposed Changes

### 1. New Dependencies
- Add `elevenlabs` Python package to requirements.txt
- Update documentation for API key configuration

### 2. Voice Engine Selection
- Add command-line option to choose between `edge-tts` (default) and `elevenlabs`
- Example: `python3 md-convo2mp3.py INPUT-CONVO.md --engine elevenlabs`

### 3. Voice Mapping
- Create ElevenLabs voice mappings for ALEX and JORDAN speakers
- Allow custom voice selection via configuration or CLI args

### 4. Configuration
- Support ElevenLabs API key via environment variable (`ELEVEN_API_KEY`)
- Handle API rate limits and error responses gracefully

### 5. Code Structure
- Extract TTS functionality into separate classes/modules
- Implement common interface for both TTS engines
- Maintain backward compatibility with existing edge-tts workflow

## Implementation Notes
- Reference: https://elevenlabs.io/docs/quickstart
- Preserve existing 300ms pause logic between speaker turns
- Maintain speech rate adjustments (currently +25%)
- Keep temporary file cleanup behavior

## Testing Considerations
- Test with various conversation lengths
- Verify audio quality compared to edge-tts
- Test API error handling and fallback scenarios
- Ensure piping workflow still functions correctly

## Documentation Updates
- Update CLAUDE.md with new engine option
- Add ElevenLabs setup instructions
- Document voice selection options