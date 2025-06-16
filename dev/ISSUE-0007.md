# ISSUE-0007: Add Comprehensive Type Hints

**Priority**: MEDIUM  
**Type**: Code Quality & Developer Experience  
**Effort**: 2-3 hours  

## Problem

The current codebase lacks type hints throughout, which results in:
- Poor IDE support and autocompletion
- Difficulty catching type-related bugs
- Reduced code maintainability
- No static type checking
- Poor documentation of function signatures

## Requirements

1. Add type hints to all functions and methods
2. Use modern typing features (Union → `|`, Optional → `| None`)
3. Create type aliases for common types
4. Configure mypy for strict type checking
5. Add py.typed marker for library distribution
6. Ensure compatibility with Python 3.8+

## Implementation Details

### Step 1: Create Type Definitions

Create `src/convo/types.py`:
```python
"""Type definitions for the convo package."""

from typing import List, Tuple, Dict, Any, Optional, Union, Protocol
from pathlib import Path

# Type aliases
SpeakerName = str
Text = str
Conversation = List[Tuple[SpeakerName, Text]]
AudioPath = Union[str, Path]
URL = str
HTMLContent = str

# Configuration types
ConfigDict = Dict[str, Any]
VoiceMapping = Dict[SpeakerName, str]

# Protocol for TTS engines
class TTSEngine(Protocol):
    """Protocol for text-to-speech engines."""
    
    def generate_audio(self, text: str, speaker: str, output_path: AudioPath) -> None:
        """Generate audio for given text."""
        ...
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices."""
        ...

# API response types
class APIResponse(Protocol):
    """Protocol for API responses."""
    content: List[Any]
    
class MessageContent(Protocol):
    """Protocol for message content."""
    text: str
```

### Step 2: Add Type Hints to Core Modules

Update `src/convo/validators.py`:
```python
"""Input validation and sanitization utilities."""

import re
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Optional
import bleach

from .types import URL, SpeakerName, Text
from .exceptions import ValidationError

def validate_url(url: URL, allowed_schemes: Optional[List[str]] = None) -> URL:
    """Validate and normalize URL.
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: ['http', 'https'])
    
    Returns:
        Normalized URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    try:
        parsed = urlparse(url)
        
        if not parsed.scheme:
            raise ValidationError("URL must include scheme (http:// or https://)")
            
        if parsed.scheme not in allowed_schemes:
            raise ValidationError(f"URL scheme must be one of: {allowed_schemes}")
            
        if not parsed.netloc:
            raise ValidationError("URL must include domain")
            
        # Prevent SSRF attacks - block internal IPs
        if re.match(r'^(localhost|127\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)', parsed.netloc):
            raise ValidationError("Internal URLs are not allowed")
            
        return url
        
    except Exception as e:
        raise ValidationError(f"Invalid URL: {e}") from e

def validate_file_path(path: str, base_dir: Optional[Path] = None) -> Path:
    """Validate file path is safe and within bounds.
    
    Args:
        path: Path to validate
        base_dir: Base directory to restrict access to
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If path is unsafe
    """
    try:
        file_path = Path(path).resolve()
        
        if not file_path.exists():
            raise ValidationError(f"Path does not exist: {path}")
        
        if base_dir:
            base_dir = Path(base_dir).resolve()
            if not str(file_path).startswith(str(base_dir)):
                raise ValidationError("Path is outside allowed directory")
                
        sensitive_patterns = ['.env', '.git', 'id_rsa', '.ssh', '.aws']
        if any(pattern in str(file_path) for pattern in sensitive_patterns):
            raise ValidationError("Access to sensitive files is not allowed")
            
        return file_path
        
    except Exception as e:
        raise ValidationError(f"Invalid file path: {e}") from e

def sanitize_html(html: HTMLContent) -> HTMLContent:
    """Sanitize HTML content to prevent XSS.
    
    Args:
        html: HTML content to sanitize
        
    Returns:
        Sanitized HTML
    """
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    allowed_attributes: Dict[str, List[str]] = {}
    
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_speaker_name(name: str) -> SpeakerName:
    """Validate speaker name for safety.
    
    Args:
        name: Speaker name to validate
        
    Returns:
        Validated speaker name
        
    Raises:
        ValidationError: If name is invalid
    """
    if not re.match(r'^[A-Za-z0-9\s\-_]+$', name):
        raise ValidationError("Speaker name contains invalid characters")
        
    if len(name) > 50:
        raise ValidationError("Speaker name too long (max 50 characters)")
        
    return name.strip()

def sanitize_text_for_tts(text: str) -> Text:
    """Sanitize text for TTS processing.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for TTS
    """
    dangerous_chars = ['$', '`', '\\', '\n', '\r', '\0']
    for char in dangerous_chars:
        text = text.replace(char, ' ')
    
    text = ' '.join(text.split())
    
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length] + "..."
        
    return text
```

Update `src/convo/converters/parser.py`:
```python
"""Conversation parsing utilities."""

import re
from pathlib import Path
from typing import TextIO

from ..types import Conversation, SpeakerName, Text
from ..validators import validate_file_path, validate_speaker_name, sanitize_text_for_tts
from ..exceptions import FileOperationError, ValidationError

def parse_conversation(file_path: str) -> Conversation:
    """Parse conversation from markdown file.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        List of (speaker, text) tuples
        
    Raises:
        FileOperationError: If file cannot be read
        ValidationError: If conversation format is invalid
    """
    validated_path = validate_file_path(file_path, base_dir=Path.cwd())
    
    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise FileOperationError(f"Unable to read file (encoding issue): {file_path}") from e
    except PermissionError as e:
        raise FileOperationError(f"Permission denied: {file_path}") from e
    
    if not content.strip():
        raise FileOperationError(f"File is empty: {file_path}")
    
    return _parse_conversation_content(content)

def _parse_conversation_content(content: str) -> Conversation:
    """Parse conversation content from markdown string.
    
    Args:
        content: Markdown content
        
    Returns:
        List of (speaker, text) tuples
        
    Raises:
        ValidationError: If no valid conversation entries found
    """
    pattern = r'\*\*([A-Z][A-Z0-9_]{0,49}):\*\*\s+(.+?)(?=\*\*[A-Z]|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    validated_conversation: Conversation = []
    
    for speaker, text in matches:
        try:
            validated_speaker = validate_speaker_name(speaker)
            sanitized_text = sanitize_text_for_tts(text.strip())
            
            if sanitized_text:
                validated_conversation.append((validated_speaker, sanitized_text))
        except ValidationError:
            continue  # Skip invalid entries
    
    if not validated_conversation:
        raise ValidationError("No valid conversation entries found")
        
    return validated_conversation

def parse_conversation_from_string(content: str) -> Conversation:
    """Parse conversation from string content.
    
    Args:
        content: Markdown conversation content
        
    Returns:
        List of (speaker, text) tuples
        
    Raises:
        ValidationError: If conversation format is invalid
    """
    return _parse_conversation_content(content)
```

Update `src/convo/tts/base.py`:
```python
"""Base classes for TTS engines."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..types import TTSEngine, SpeakerName, Text, AudioPath, VoiceMapping

class BaseTTS(ABC):
    """Base class for text-to-speech engines."""
    
    def __init__(self, voice_mapping: Optional[VoiceMapping] = None) -> None:
        """Initialize TTS engine.
        
        Args:
            voice_mapping: Mapping of speaker names to voice IDs
        """
        self.voice_mapping = voice_mapping or self._get_default_voice_mapping()
    
    @abstractmethod
    def _get_default_voice_mapping(self) -> VoiceMapping:
        """Get default voice mapping for this engine."""
        pass
    
    @abstractmethod
    async def generate_audio(self, text: Text, speaker: SpeakerName, output_path: AudioPath) -> None:
        """Generate audio for given text.
        
        Args:
            text: Text to convert to speech
            speaker: Speaker name
            output_path: Path to save audio file
            
        Raises:
            TTSError: If audio generation fails
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Get list of available voices.
        
        Returns:
            List of voice IDs
        """
        pass
    
    def get_voice_for_speaker(self, speaker: SpeakerName) -> str:
        """Get voice ID for speaker.
        
        Args:
            speaker: Speaker name
            
        Returns:
            Voice ID for the speaker
        """
        return self.voice_mapping.get(speaker, self._get_default_voice())
    
    @abstractmethod
    def _get_default_voice(self) -> str:
        """Get default voice ID."""
        pass
```

### Step 3: Configure mypy

Update `pyproject.toml` mypy section:
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_codes = true
namespace_packages = true
mypy_path = "src"

[[tool.mypy.overrides]]
module = [
    "edge_tts.*",
    "pyttsx3.*",
    "pydub.*",
    "anthropic.*",
]
ignore_missing_imports = true
```

### Step 4: Add py.typed Marker

Create `src/convo/py.typed` (empty file):
```bash
touch src/convo/py.typed
```

### Step 5: Update Function Signatures Throughout

Example for `src/convo/web/fetcher.py`:
```python
"""Web content fetching utilities."""

import requests
from bs4 import BeautifulSoup, Tag
from typing import Tuple, Optional
import logging

from ..types import URL, HTMLContent, Text
from ..validators import validate_url, sanitize_html
from ..exceptions import NetworkError, ValidationError

logger = logging.getLogger(__name__)

def fetch_article(url: URL, timeout: int = 30) -> Tuple[str, Text]:
    """Fetch and parse article from URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (title, content)
        
    Raises:
        NetworkError: If fetching fails
        ValidationError: If URL is invalid
    """
    validated_url = validate_url(url)
    
    try:
        response = requests.get(
            validated_url, 
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; ConvoBot/1.0)'}
        )
        response.raise_for_status()
        
        safe_html = sanitize_html(response.text)
        soup = BeautifulSoup(safe_html, 'html.parser')
        
        title = _extract_title(soup)
        content = _extract_content(soup)
        
        return title, content
        
    except requests.exceptions.SSLError as e:
        raise NetworkError("SSL certificate verification failed") from e
    except requests.exceptions.Timeout as e:
        raise NetworkError("Request timed out") from e
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Failed to fetch article: {e}") from e

def _extract_title(soup: BeautifulSoup) -> str:
    """Extract title from HTML soup.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Article title
    """
    title_tag: Optional[Tag] = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "Untitled"
    
    if len(title) > 200:
        title = title[:197] + "..."
        
    return title

def _extract_content(soup: BeautifulSoup) -> Text:
    """Extract main content from HTML soup.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Article content
    """
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Try to find main content
    content_selectors = [
        'article',
        '.post-content',
        '.entry-content', 
        '.content',
        'main',
        '#content'
    ]
    
    content_element: Optional[Tag] = None
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            break
    
    if not content_element:
        content_element = soup.find('body') or soup
    
    return content_element.get_text(separator=' ', strip=True)
```

## Acceptance Criteria

- [ ] All functions have type hints
- [ ] Type aliases are defined for common types  
- [ ] mypy passes with no errors on strict settings
- [ ] py.typed marker is included
- [ ] Protocol classes are defined for interfaces
- [ ] Generic types are used appropriately
- [ ] Backward compatibility with Python 3.8+
- [ ] IDE autocompletion works correctly

## Testing Type Hints

```bash
# Run mypy type checking
mypy src/

# Test with different Python versions
tox -e py38,py39,py310,py311,py312

# Check package typing in consuming code
python -c "import convo; reveal_type(convo.ConversationParser)"
```

## Type Checking in CI

Add to `.github/workflows/ci.yml`:
```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy src/
```

## Benefits

1. **Better IDE Support**: Autocompletion, error detection
2. **Early Bug Detection**: Catch type errors before runtime
3. **Self-Documenting Code**: Type hints serve as documentation
4. **Refactoring Safety**: Types help ensure changes don't break interfaces
5. **Library User Experience**: Better experience for package users

## References

- [Python Type Hints PEP 484](https://peps.python.org/pep-0484/)
- [typing module documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Protocols PEP 544](https://peps.python.org/pep-0544/)