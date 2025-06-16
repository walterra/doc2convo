# ISSUE-0004: Add Input Validation and Sanitization

**Priority**: CRITICAL  
**Type**: Security  
**Effort**: 2 hours  

## Problem

The codebase lacks input validation and sanitization, particularly in:
- HTML content parsing in `url2convo.py` (potential XSS if output is ever rendered)
- File path handling (potential directory traversal)
- URL validation (could fetch malicious content)
- Speaker name parsing (injection into TTS commands)

Without proper validation, the application is vulnerable to various injection attacks and may behave unpredictably with malformed input.

## Security Risks

1. **Directory Traversal**: Unvalidated file paths could access system files
2. **SSRF**: Unvalidated URLs could access internal resources  
3. **Command Injection**: Unvalidated speaker names in TTS engines
4. **Content Injection**: Malicious HTML could be processed

## Requirements

1. Validate all user inputs before processing
2. Sanitize HTML content from web sources
3. Validate file paths stay within expected directories
4. Validate URLs are well-formed and use allowed schemes
5. Sanitize speaker names and text content for TTS
6. Add rate limiting for API calls

## Implementation Details

### Step 1: Create Validation Module

Create `validators.py`:
```python
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional
import bleach

class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass

def validate_url(url: str, allowed_schemes: list = None) -> str:
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
        
        # Check if path exists
        if not file_path.exists():
            raise ValidationError(f"Path does not exist: {path}")
        
        # Ensure path is within base directory if specified
        if base_dir:
            base_dir = Path(base_dir).resolve()
            if not str(file_path).startswith(str(base_dir)):
                raise ValidationError("Path is outside allowed directory")
                
        # Block access to sensitive files
        sensitive_patterns = ['.env', '.git', 'id_rsa', '.ssh', '.aws']
        if any(pattern in str(file_path) for pattern in sensitive_patterns):
            raise ValidationError("Access to sensitive files is not allowed")
            
        return file_path
        
    except Exception as e:
        raise ValidationError(f"Invalid file path: {e}") from e

def sanitize_html(html: str) -> str:
    """Sanitize HTML content to prevent XSS.
    
    Args:
        html: HTML content to sanitize
        
    Returns:
        Sanitized HTML
    """
    # Allow only basic formatting tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    allowed_attributes = {}
    
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_speaker_name(name: str) -> str:
    """Validate speaker name for safety.
    
    Args:
        name: Speaker name to validate
        
    Returns:
        Validated speaker name
        
    Raises:
        ValidationError: If name is invalid
    """
    # Allow only alphanumeric and basic punctuation
    if not re.match(r'^[A-Za-z0-9\s\-_]+$', name):
        raise ValidationError("Speaker name contains invalid characters")
        
    # Limit length
    if len(name) > 50:
        raise ValidationError("Speaker name too long (max 50 characters)")
        
    return name.strip()

def sanitize_text_for_tts(text: str) -> str:
    """Sanitize text for TTS processing.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for TTS
    """
    # Remove potential command injection characters
    dangerous_chars = ['$', '`', '\\', '\n', '\r', '\0']
    for char in dangerous_chars:
        text = text.replace(char, ' ')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Limit length to prevent abuse
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length] + "..."
        
    return text
```

### Step 2: Update url2convo.py with Validation

```python
from validators import validate_url, sanitize_html, ValidationError

def fetch_article(url):
    """Fetch and parse article from URL with validation."""
    try:
        # Validate URL before fetching
        validated_url = validate_url(url)
        
        # Add timeout to prevent hanging
        response = requests.get(validated_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; ConvoBot/1.0)'
        })
        response.raise_for_status()
        
        # Sanitize HTML before parsing
        safe_html = sanitize_html(response.text)
        soup = BeautifulSoup(safe_html, 'html.parser')
        
        # Extract content safely
        title = soup.find('title')
        title = title.text.strip() if title else "Untitled"
        
        # Validate title length
        if len(title) > 200:
            title = title[:197] + "..."
            
        return title, extract_content(soup)
        
    except ValidationError as e:
        raise
    except requests.exceptions.SSLError:
        raise ValidationError("SSL certificate verification failed")
    except requests.exceptions.Timeout:
        raise ValidationError("Request timed out")
    except Exception as e:
        raise ValidationError(f"Failed to fetch article: {e}")
```

### Step 3: Update Conversation Parsing with Validation

```python
from validators import validate_speaker_name, sanitize_text_for_tts, validate_file_path

def parse_conversation(file_path):
    """Parse conversation from markdown file with validation."""
    # Validate file path
    validated_path = validate_file_path(file_path, base_dir=Path.cwd())
    
    with open(validated_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Updated regex to be more strict
    pattern = r'\*\*([A-Z][A-Z0-9_]{0,49}):\*\*\s+(.+?)(?=\*\*[A-Z]|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    validated_conversation = []
    for speaker, text in matches:
        # Validate speaker name
        validated_speaker = validate_speaker_name(speaker)
        
        # Sanitize text for TTS
        sanitized_text = sanitize_text_for_tts(text.strip())
        
        if sanitized_text:  # Only add non-empty text
            validated_conversation.append((validated_speaker, sanitized_text))
    
    if not validated_conversation:
        raise ValidationError("No valid conversation entries found")
        
    return validated_conversation
```

### Step 4: Add Rate Limiting

```python
from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time()
            key = func.__name__
            
            # Clean old calls
            self.calls[key] = [call_time for call_time in self.calls[key] 
                              if now - call_time < self.time_window]
            
            # Check rate limit
            if len(self.calls[key]) >= self.max_calls:
                raise ValidationError(
                    f"Rate limit exceeded. Max {self.max_calls} calls per {self.time_window} seconds"
                )
            
            # Record call
            self.calls[key].append(now)
            
            return func(*args, **kwargs)
        return wrapper

# Apply rate limiting to API calls
@RateLimiter(max_calls=10, time_window=60)  # 10 calls per minute
def generate_conversation(title, content, url, system_prompt=None):
    # ... existing implementation
```

## Acceptance Criteria

- [ ] All user inputs are validated before use
- [ ] File paths are restricted to safe directories
- [ ] URLs are validated and SSRF protection is in place
- [ ] HTML content is sanitized to prevent XSS
- [ ] Speaker names and text are sanitized for TTS
- [ ] Rate limiting prevents API abuse
- [ ] Clear error messages for validation failures
- [ ] No security warnings from security scanners

## Testing

```python
def test_url_validation():
    """Test URL validation."""
    # Valid URLs
    assert validate_url("https://example.com") == "https://example.com"
    
    # Invalid URLs
    with pytest.raises(ValidationError):
        validate_url("not-a-url")
    
    # Blocked internal URLs
    with pytest.raises(ValidationError):
        validate_url("http://localhost/admin")
    with pytest.raises(ValidationError):
        validate_url("http://192.168.1.1/")

def test_path_traversal_prevention():
    """Test path traversal attack prevention."""
    with pytest.raises(ValidationError):
        validate_file_path("../../../etc/passwd")
    
    with pytest.raises(ValidationError):
        validate_file_path("/etc/passwd", base_dir="/home/user")

def test_speaker_name_validation():
    """Test speaker name validation."""
    assert validate_speaker_name("ALEX") == "ALEX"
    assert validate_speaker_name("User_123") == "User_123"
    
    with pytest.raises(ValidationError):
        validate_speaker_name("'; DROP TABLE users; --")

def test_tts_text_sanitization():
    """Test TTS text sanitization."""
    dangerous = "Hello $USER `rm -rf /`"
    safe = sanitize_text_for_tts(dangerous)
    assert "$" not in safe
    assert "`" not in safe
```

## References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Python bleach library](https://bleach.readthedocs.io/)
- [SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)