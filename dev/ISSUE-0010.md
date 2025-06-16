# ISSUE-0010: Add Configuration Management

**Priority**: MEDIUM  
**Type**: User Experience & Flexibility  
**Effort**: 2-3 hours  

## Problem

The current codebase has hardcoded values throughout:
- Hardcoded file names (`DAILY-CONVO.md`, `podcast.mp3`)
- Hardcoded voice mappings
- No configuration file support
- Limited command-line options
- No environment variable documentation

This makes the tool inflexible and difficult to customize for different use cases.

## Requirements

1. Create configuration system with multiple sources
2. Support configuration files (YAML, TOML, JSON)
3. Environment variable support
4. Command-line argument override
5. Configuration validation with Pydantic
6. Default configuration with sensible defaults
7. Configuration file generation/initialization

## Implementation Details

### Step 1: Configuration Schema

Create `src/convo/config.py`:
```python
"""Configuration management for convo package."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
import yaml
import toml
import json

class TTSConfig(BaseModel):
    """TTS engine configuration."""
    
    engine: str = Field(default="edge", description="TTS engine to use")
    voices: Dict[str, str] = Field(
        default_factory=lambda: {
            "ALEX": "en-US-ChristopherNeural",
            "JORDAN": "en-US-JennyNeural",
            "SAM": "en-US-EricNeural",
            "TAYLOR": "en-US-AriaNeural"
        },
        description="Voice mapping for speakers"
    )
    rate: str = Field(default="+0%", description="Speech rate adjustment")
    volume: str = Field(default="+0%", description="Volume adjustment")
    pitch: str = Field(default="+0Hz", description="Pitch adjustment")
    
    @validator('engine')
    def validate_engine(cls, v):
        if v not in ['edge', 'pyttsx3']:
            raise ValueError(f"Invalid TTS engine: {v}")
        return v

class WebConfig(BaseModel):
    """Web fetching configuration."""
    
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; ConvoBot/1.0)",
        description="User agent for web requests"
    )
    max_content_length: int = Field(
        default=10_000_000,  # 10MB
        ge=1000,
        description="Maximum content length to fetch"
    )
    allowed_domains: Optional[List[str]] = Field(
        default=None,
        description="Allowed domains (if specified, only these domains are allowed)"
    )
    blocked_domains: List[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "10.", "192.168.", "172."],
        description="Blocked domains for security"
    )

class AudioConfig(BaseModel):
    """Audio processing configuration."""
    
    format: str = Field(default="mp3", description="Output audio format")
    bitrate: str = Field(default="128k", description="Audio bitrate")
    sample_rate: int = Field(default=22050, gt=0, description="Sample rate in Hz")
    pause_duration: float = Field(default=0.3, ge=0.0, le=5.0, description="Pause between speakers in seconds")
    fade_in: float = Field(default=0.1, ge=0.0, le=2.0, description="Fade in duration")
    fade_out: float = Field(default=0.1, ge=0.0, le=2.0, description="Fade out duration")

class APIConfig(BaseModel):
    """API configuration."""
    
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    max_tokens: int = Field(default=8000, ge=100, le=100000, description="Maximum tokens for API requests")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Response temperature")
    
    @validator('anthropic_api_key', pre=True, always=True)
    def get_api_key(cls, v):
        # Try provided value, then environment variable
        return v or os.getenv('ANTHROPIC_API_KEY')

class ConvoConfig(BaseModel):
    """Main configuration model."""
    
    # Subsection configurations
    tts: TTSConfig = Field(default_factory=TTSConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    
    # Global settings
    output_dir: Path = Field(default=Path.cwd(), description="Default output directory")
    temp_dir: Optional[Path] = Field(default=None, description="Temporary directory (uses system temp if None)")
    log_level: str = Field(default="INFO", description="Logging level")
    verbose: bool = Field(default=False, description="Enable verbose output")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()
    
    @validator('temp_dir', pre=True)
    def validate_temp_dir(cls, v):
        if v is None:
            return None
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        """Pydantic configuration."""
        env_prefix = 'CONVO_'
        env_nested_delimiter = '__'
        case_sensitive = False
```

### Step 2: Configuration Loading

Add to `config.py`:
```python
def load_config(config_path: Optional[Union[str, Path]] = None) -> ConvoConfig:
    """Load configuration from various sources.
    
    Order of precedence (highest to lowest):
    1. Command-line arguments (handled by CLI)
    2. Environment variables
    3. Configuration file
    4. Default values
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Loaded configuration
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    config_data = {}
    
    # Try to find config file if not specified
    if config_path is None:
        config_path = find_config_file()
    
    # Load from config file if exists
    if config_path and Path(config_path).exists():
        config_data = load_config_file(config_path)
    
    try:
        # Pydantic will handle environment variables automatically
        return ConvoConfig(**config_data)
    except Exception as e:
        from .exceptions import ConfigurationError
        raise ConfigurationError(f"Invalid configuration: {e}") from e

def find_config_file() -> Optional[Path]:
    """Find configuration file in standard locations.
    
    Search order:
    1. ./convo.yaml
    2. ./convo.toml
    3. ~/.convo/config.yaml
    4. ~/.convo/config.toml
    5. ~/.config/convo/config.yaml
    
    Returns:
        Path to configuration file or None
    """
    search_paths = [
        Path.cwd() / "convo.yaml",
        Path.cwd() / "convo.toml", 
        Path.home() / ".convo" / "config.yaml",
        Path.home() / ".convo" / "config.toml",
        Path.home() / ".config" / "convo" / "config.yaml",
    ]
    
    for path in search_paths:
        if path.exists():
            return path
    
    return None

def load_config_file(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If file cannot be loaded
    """
    path = Path(config_path)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                return yaml.safe_load(f) or {}
            elif path.suffix.lower() == '.toml':
                return toml.load(f)
            elif path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
                
    except Exception as e:
        from .exceptions import ConfigurationError
        raise ConfigurationError(f"Failed to load config file {path}: {e}") from e

def save_config(config: ConvoConfig, config_path: Union[str, Path], format: str = 'yaml'):
    """Save configuration to file.
    
    Args:
        config: Configuration to save
        config_path: Path to save configuration
        format: File format ('yaml', 'toml', 'json')
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    config_dict = config.dict()
    
    with open(path, 'w', encoding='utf-8') as f:
        if format.lower() == 'yaml':
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif format.lower() == 'toml':
            toml.dump(config_dict, f)
        elif format.lower() == 'json':
            json.dump(config_dict, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

### Step 3: CLI Integration

Update `src/convo/cli.py`:
```python
@click.group()
@click.version_option(version=__version__)
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--output-dir', type=click.Path(), help='Output directory')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), help='Logging level')
@click.pass_context
def main(ctx, config: Optional[str], verbose: bool, output_dir: Optional[str], log_level: Optional[str]):
    """Convert web articles and conversations to audio podcasts."""
    ctx.ensure_object(dict)
    
    # Load configuration
    try:
        ctx.obj['config'] = load_config(config)
    except ConfigurationError as e:
        click.echo(f"Configuration error: {e}", err=True)
        ctx.exit(1)
    
    # Override with CLI arguments
    if verbose:
        ctx.obj['config'].verbose = True
        ctx.obj['config'].log_level = 'DEBUG'
    
    if output_dir:
        ctx.obj['config'].output_dir = Path(output_dir)
    
    if log_level:
        ctx.obj['config'].log_level = log_level
    
    # Set up logging
    setup_logging(ctx.obj['config'])

@main.command()
@click.option('--format', type=click.Choice(['yaml', 'toml', 'json']), default='yaml', help='Configuration format')
@click.option('--output', '-o', default='convo.yaml', help='Output file path')
def init_config(format: str, output: str):
    """Initialize configuration file with defaults."""
    try:
        default_config = ConvoConfig()
        save_config(default_config, output, format)
        click.echo(f"✅ Configuration saved to: {output}")
        click.echo("Edit the file to customize your settings.")
    except Exception as e:
        click.echo(f"❌ Failed to create config: {e}", err=True)
        raise click.Abort()

@main.command()
@click.pass_context
def show_config(ctx):
    """Show current configuration."""
    config = ctx.obj['config']
    
    # Convert to dict and pretty print
    config_dict = config.dict()
    click.echo(yaml.dump(config_dict, default_flow_style=False, indent=2))
```

### Step 4: Default Configuration Files

Create `templates/convo.yaml`:
```yaml
# Convo Configuration File
# This file contains default settings for the convo package

# Text-to-Speech Configuration
tts:
  engine: edge  # Options: edge, pyttsx3
  voices:
    ALEX: en-US-ChristopherNeural
    JORDAN: en-US-JennyNeural
    SAM: en-US-EricNeural
    TAYLOR: en-US-AriaNeural
  rate: "+0%"    # Speech rate: -50% to +200%
  volume: "+0%"  # Volume: -50% to +50%
  pitch: "+0Hz"  # Pitch: -200Hz to +200Hz

# Web Fetching Configuration
web:
  timeout: 30
  user_agent: "Mozilla/5.0 (compatible; ConvoBot/1.0)"
  max_content_length: 10000000  # 10MB
  allowed_domains: null  # null = allow all (except blocked)
  blocked_domains:
    - localhost
    - 127.0.0.1
    - "10."
    - "192.168."
    - "172."

# Audio Processing Configuration
audio:
  format: mp3
  bitrate: 128k
  sample_rate: 22050
  pause_duration: 0.3  # Seconds between speakers
  fade_in: 0.1
  fade_out: 0.1

# API Configuration
api:
  anthropic_api_key: null  # Set via ANTHROPIC_API_KEY env var
  max_tokens: 8000
  model: claude-3-5-sonnet-20241022
  temperature: 0.7

# Global Settings
output_dir: "."
temp_dir: null  # Uses system temp directory
log_level: INFO
verbose: false
```

### Step 5: Environment Variable Documentation

Create `docs/configuration.md`:
```markdown
# Configuration

Convo supports multiple configuration methods with the following precedence:

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## Configuration File

Create a configuration file in YAML, TOML, or JSON format:

```bash
# Initialize default configuration
convo init-config --format yaml --output convo.yaml

# Show current configuration
convo show-config
```

### File Locations

Convo searches for configuration files in this order:

1. `./convo.yaml` or `./convo.toml`
2. `~/.convo/config.yaml` or `~/.convo/config.toml`
3. `~/.config/convo/config.yaml`

## Environment Variables

All configuration options can be set via environment variables using the `CONVO_` prefix:

### Basic Settings
```bash
export CONVO_LOG_LEVEL=DEBUG
export CONVO_VERBOSE=true
export CONVO_OUTPUT_DIR=/path/to/output
```

### TTS Settings
```bash
export CONVO_TTS__ENGINE=edge
export CONVO_TTS__RATE="+20%"
export CONVO_TTS__VOLUME="+10%"
```

### API Settings  
```bash
export CONVO_API__ANTHROPIC_API_KEY=your-api-key
export CONVO_API__MAX_TOKENS=4000
export CONVO_API__MODEL=claude-3-haiku-20240307
```

### Web Settings
```bash
export CONVO_WEB__TIMEOUT=60
export CONVO_WEB__USER_AGENT="Custom Bot 1.0"
```

### Audio Settings
```bash
export CONVO_AUDIO__FORMAT=wav
export CONVO_AUDIO__BITRATE=192k
export CONVO_AUDIO__PAUSE_DURATION=0.5
```

## Command-Line Overrides

Common CLI options that override configuration:

```bash
# Override output directory
convo url "https://example.com" --output-dir /tmp

# Override log level
convo file chat.md --log-level DEBUG

# Use specific config file
convo url "https://example.com" --config /path/to/config.yaml
```

## Voice Customization

Customize voices by speaker name:

```yaml
tts:
  voices:
    ALEX: en-US-ChristopherNeural
    JORDAN: en-US-JennyNeural
    EXPERT: en-GB-RyanNeural
    HOST: en-AU-NatashaNeural
```

Available voices depend on your TTS engine:
- Edge TTS: [Microsoft Neural Voices](https://speech.microsoft.com/portal/voicegallery)
- pyttsx3: System voices (varies by OS)

## Validation

Configuration is validated on load:
- Invalid values will show helpful error messages
- Required fields are enforced
- Ranges and formats are checked

Example validation error:
```
Configuration error: Invalid TTS engine: unknown_engine
Valid options: edge, pyttsx3
```
```

## Acceptance Criteria

- [ ] Configuration system supports multiple file formats
- [ ] Environment variable support with proper naming
- [ ] CLI arguments override configuration settings
- [ ] Configuration validation with clear error messages
- [ ] Default configuration with sensible values
- [ ] Configuration file initialization command
- [ ] Documentation covers all configuration options
- [ ] Backward compatibility maintained during transition

## Testing Configuration

```python
def test_config_loading():
    """Test configuration loading from different sources."""
    # Test default configuration
    config = ConvoConfig()
    assert config.tts.engine == "edge"
    
    # Test environment variable override
    with patch.dict(os.environ, {'CONVO_TTS__ENGINE': 'pyttsx3'}):
        config = ConvoConfig()
        assert config.tts.engine == "pyttsx3"
    
    # Test config file loading
    config_data = {"tts": {"engine": "pyttsx3"}}
    with patch('convo.config.load_config_file', return_value=config_data):
        config = load_config("test.yaml")
        assert config.tts.engine == "pyttsx3"

def test_config_validation():
    """Test configuration validation."""
    with pytest.raises(ValidationError):
        ConvoConfig(tts={"engine": "invalid_engine"})
    
    with pytest.raises(ValidationError):
        ConvoConfig(web={"timeout": -1})
```

## Migration Guide

For users upgrading from hardcoded values:

1. Run `convo init-config` to create default configuration
2. Edit the configuration file to match your previous usage
3. Remove any hardcoded values from scripts
4. Use environment variables in deployment scripts

## References

- [Pydantic Configuration](https://pydantic-docs.helpmanual.io/usage/settings/)
- [Click Configuration](https://click.palletsprojects.com/en/8.1.x/options/#values-from-environment-variables)
- [YAML Format](https://yaml.org/spec/1.2/spec.html)
- [TOML Format](https://toml.io/en/)