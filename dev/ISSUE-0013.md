# ISSUE-0013: Add Orpheus TTS Support via LMStudio

**Priority**: MEDIUM  
**Type**: Feature Enhancement  
**Effort**: 4-6 hours  

## Problem

The current TTS implementation only supports Microsoft Edge neural voices, which requires internet connectivity and Microsoft services. Local TTS solutions would provide:

- Offline operation capability
- Privacy - no external API calls
- Custom voice control
- Reduced latency for local processing
- Independence from cloud service availability

[Orpheus TTS](https://github.com/isaiahbjork/orpheus-tts-local) via LMStudio provides a local neural TTS solution that could complement the existing Edge TTS implementation.

## Requirements

1. Add Orpheus TTS as an optional TTS backend alongside existing Edge TTS
2. Support voice configuration for Orpheus models
3. Maintain compatibility with existing conversation format
4. Provide fallback mechanism if Orpheus is unavailable
5. Add configuration options for Orpheus server endpoint
6. Update documentation with setup instructions

## Implementation Details

### Step 1: Add Orpheus Dependencies

Update `requirements.txt`:
```txt
# Add optional Orpheus support
requests>=2.31.0  # For API calls to LMStudio/Orpheus
```

### Step 2: Create Orpheus TTS Backend

Create new file `orpheus_tts.py`:
```python
#!/usr/bin/env python3
"""Orpheus TTS backend for local neural text-to-speech via LMStudio."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests
import logging

logger = logging.getLogger(__name__)

class OrpheusTTSBackend:
    """Orpheus TTS backend using LMStudio API."""
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234",
                 model_name: Optional[str] = None,
                 voice_mapping: Optional[Dict[str, str]] = None):
        """Initialize Orpheus TTS backend.
        
        Args:
            base_url: LMStudio server URL
            model_name: Specific model to use
            voice_mapping: Speaker to voice mapping
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.voice_mapping = voice_mapping or {
            'ALEX': 'male_voice_1',
            'JORDAN': 'female_voice_1'
        }
    
    async def synthesize_speech(self, text: str, voice: str) -> bytes:
        """Synthesize speech using Orpheus TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            
        Returns:
            Audio data as bytes
        """
        try:
            # Map speaker to Orpheus voice
            orpheus_voice = self.voice_mapping.get(voice, voice)
            
            # Prepare API request
            payload = {
                "text": text,
                "voice": orpheus_voice,
                "speed": 1.0,
                "pitch": 1.0
            }
            
            if self.model_name:
                payload["model"] = self.model_name
            
            # Make API call to LMStudio/Orpheus
            response = requests.post(
                f"{self.base_url}/v1/tts",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Return audio data
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Orpheus TTS request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Orpheus TTS synthesis failed: {e}")
            raise
    
    def check_availability(self) -> bool:
        """Check if Orpheus TTS server is available."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available voices from Orpheus server."""
        try:
            response = requests.get(f"{self.base_url}/v1/voices", timeout=5)
            if response.status_code == 200:
                voices_data = response.json()
                return {voice['id']: voice['name'] for voice in voices_data.get('voices', [])}
            return {}
        except requests.exceptions.RequestException:
            logger.warning("Could not fetch available voices from Orpheus")
            return self.voice_mapping
```

### Step 3: Update Main TTS Module

Modify `md-convo2mp3.py` to support multiple TTS backends:

```python
# Add imports
from orpheus_tts import OrpheusTTSBackend

# Add backend selection logic
def create_tts_backend(backend_type: str = "edge", **kwargs):
    """Create TTS backend based on type."""
    if backend_type.lower() == "orpheus":
        return OrpheusTTSBackend(**kwargs)
    elif backend_type.lower() == "edge":
        # Return existing Edge TTS implementation
        return EdgeTTSBackend(**kwargs)
    else:
        raise ValueError(f"Unknown TTS backend: {backend_type}")

# Update main function
async def main():
    parser = argparse.ArgumentParser(description="Convert conversation to audio")
    parser.add_argument("input_file", help="Input markdown file")
    parser.add_argument("-o", "--output", help="Output audio file")
    parser.add_argument("--tts-backend", choices=["edge", "orpheus"], 
                       default="edge", help="TTS backend to use")
    parser.add_argument("--orpheus-url", default="http://localhost:1234",
                       help="Orpheus/LMStudio server URL")
    parser.add_argument("--orpheus-model", help="Specific Orpheus model to use")
    
    args = parser.parse_args()
    
    # Create TTS backend
    if args.tts_backend == "orpheus":
        tts_backend = create_tts_backend("orpheus", 
                                       base_url=args.orpheus_url,
                                       model_name=args.orpheus_model)
        
        # Check availability
        if not tts_backend.check_availability():
            print("⚠️ Orpheus TTS server not available, falling back to Edge TTS")
            tts_backend = create_tts_backend("edge")
    else:
        tts_backend = create_tts_backend("edge")
    
    # Rest of existing logic...
```

### Step 4: Add Configuration Support

Create `config.py` for TTS backend configuration:
```python
#!/usr/bin/env python3
"""Configuration management for doc2convo."""

import os
from typing import Dict, Optional
import json
from pathlib import Path

class TTSConfig:
    """TTS configuration management."""
    
    def __init__(self):
        self.config_file = Path.home() / ".doc2convo" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Get default configuration."""
        return {
            "tts": {
                "default_backend": "edge",
                "edge": {
                    "voices": {
                        "ALEX": "en-US-ChristopherNeural",
                        "JORDAN": "en-US-JennyNeural"
                    }
                },
                "orpheus": {
                    "server_url": "http://localhost:1234",
                    "voices": {
                        "ALEX": "male_voice_1",
                        "JORDAN": "female_voice_1"
                    },
                    "model": None
                }
            }
        }
    
    def get_tts_config(self, backend: str) -> Dict:
        """Get TTS configuration for specific backend."""
        return self.config.get("tts", {}).get(backend, {})
    
    def save_config(self):
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
```

### Step 5: Update Command Line Interface

Add new command line options:
```bash
# Basic usage with Orpheus
python3 md-convo2mp3.py conversation.md --tts-backend orpheus

# With custom Orpheus server
python3 md-convo2mp3.py conversation.md --tts-backend orpheus --orpheus-url http://192.168.1.100:1234

# With specific model
python3 md-convo2mp3.py conversation.md --tts-backend orpheus --orpheus-model "neural-tts-v1"

# Fallback behavior (auto-detect)
python3 md-convo2mp3.py conversation.md --tts-backend auto
```

### Step 6: Update Documentation

Add section to CLAUDE.md:
```markdown
## TTS Backend Options

### Orpheus TTS (Local)

Orpheus TTS provides local neural text-to-speech via LMStudio:

1. **Setup LMStudio with Orpheus**:
   ```bash
   # Install LMStudio
   # Load Orpheus TTS model in LMStudio
   # Start LMStudio server on port 1234
   ```

2. **Configure Orpheus**:
   ```bash
   # Use Orpheus backend
   python3 md-convo2mp3.py conversation.md --tts-backend orpheus
   
   # Custom server URL
   python3 md-convo2mp3.py conversation.md --tts-backend orpheus --orpheus-url http://localhost:8080
   ```

3. **Voice Configuration**:
   - ALEX: male_voice_1 (configurable)
   - JORDAN: female_voice_1 (configurable)

### Edge TTS (Cloud)

Default Microsoft Edge neural voices (existing implementation).

### Backend Selection

- `--tts-backend edge`: Use Microsoft Edge TTS (default)
- `--tts-backend orpheus`: Use local Orpheus TTS
- `--tts-backend auto`: Auto-detect available backend
```

## Acceptance Criteria

- [ ] Orpheus TTS backend implemented and functional
- [ ] Seamless integration with existing conversation parsing
- [ ] Voice mapping configuration for speaker assignment
- [ ] Fallback mechanism when Orpheus unavailable
- [ ] Command line options for Orpheus configuration
- [ ] Configuration file support for persistent settings
- [ ] Documentation updated with setup instructions
- [ ] Error handling for connection failures
- [ ] Performance comparable to Edge TTS

## Testing Plan

1. **Unit Tests**:
   - Orpheus backend initialization
   - API call handling
   - Error scenarios
   - Voice mapping

2. **Integration Tests**:
   - End-to-end conversation conversion
   - Fallback behavior
   - Configuration loading

3. **Manual Testing**:
   - LMStudio setup with Orpheus
   - Various voice configurations
   - Network failure scenarios
   - Performance comparison

## Benefits

1. **Privacy**: All TTS processing happens locally
2. **Offline**: No internet dependency
3. **Customization**: Use any Orpheus-compatible voice models
4. **Performance**: Potentially faster for local processing
5. **Flexibility**: Multiple backend options for different use cases
6. **Reliability**: Local processing reduces external dependencies

## Implementation Notes

- Keep Orpheus as optional dependency to maintain lightweight installation
- Implement graceful degradation when Orpheus unavailable
- Use async/await patterns consistent with existing Edge TTS code
- Consider caching for frequently used voice configurations
- Ensure proper error messages guide users through setup process

## References

- [Orpheus TTS Local](https://github.com/isaiahbjork/orpheus-tts-local)
- [LMStudio Documentation](https://lmstudio.ai/docs)
- [TTS API Standards](https://platform.openai.com/docs/api-reference/audio/createSpeech)