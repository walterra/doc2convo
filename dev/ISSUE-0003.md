# ISSUE-0003: Add Comprehensive Error Handling

**Priority**: CRITICAL  
**Type**: Reliability & User Experience  
**Effort**: 2-3 hours

## Problem

The current codebase has minimal to no error handling. File operations, network requests, and audio generation can all fail, causing the program to crash with unhelpful error messages. This results in:

- Poor user experience
- Difficulty debugging issues
- Potential data loss
- Security implications (stack traces may reveal sensitive info)

## Affected Files

- `md-convo2mp3.py` - No error handling for TTS operations
- `text_to_speech.py` - No error handling for pyttsx3 operations
- `doc2md-convo.py` - Basic error handling but no proper exceptions

## Requirements

1. Add try/except blocks for all I/O operations
2. Create custom exception classes for different error types
3. Provide helpful error messages to users
4. Log errors appropriately (without exposing sensitive data)
5. Implement graceful degradation where possible
6. Add retry logic for transient failures

## Implementation Details

### Step 1: Create Custom Exceptions

Create `exceptions.py`:

```python
class ConvoError(Exception):
    """Base exception for convo package."""
    pass

class FileOperationError(ConvoError):
    """Raised when file operations fail."""
    pass

class TTSError(ConvoError):
    """Raised when text-to-speech operations fail."""
    pass

class NetworkError(ConvoError):
    """Raised when network operations fail."""
    pass

class APIError(ConvoError):
    """Raised when API calls fail."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class ConfigurationError(ConvoError):
    """Raised when configuration is invalid."""
    pass
```

### Step 2: Add Error Handling to File Operations

Example for `md-convo2mp3.py`:

```python
import logging
from pathlib import Path
from .exceptions import FileOperationError, TTSError

logger = logging.getLogger(__name__)

def parse_conversation(file_path):
    """Parse conversation from markdown file.

    Raises:
        FileOperationError: If file cannot be read
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileOperationError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            raise FileOperationError(f"File is empty: {file_path}")

        # Parse content...
        return parsed_content

    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading {file_path}: {e}")
        raise FileOperationError(f"Unable to read file (encoding issue): {file_path}") from e
    except PermissionError as e:
        logger.error(f"Permission denied reading {file_path}: {e}")
        raise FileOperationError(f"Permission denied: {file_path}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}")
        raise FileOperationError(f"Error reading file: {file_path}") from e
```

### Step 3: Add Error Handling to TTS Operations

```python
async def generate_audio(speaker, text, output_file):
    """Generate audio for text using edge-tts.

    Raises:
        TTSError: If audio generation fails
    """
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, VOICES[speaker])
            await communicate.save(output_file)
            return
        except Exception as e:
            logger.warning(f"TTS attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise TTSError(f"Failed to generate audio after {max_retries} attempts") from e
```

### Step 4: Add Error Handling to API Calls

```python
def generate_conversation(title, content, url, system_prompt=None):
    """Generate conversation using Claude API.

    Raises:
        ConfigurationError: If API key is missing
        APIError: If API call fails
        NetworkError: If network issues occur
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ConfigurationError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set it to your Anthropic API key."
        )

    try:
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
            system=system_prompt or DEFAULT_SYSTEM_PROMPT
        )

        return response.content[0].text

    except anthropic.APIConnectionError as e:
        logger.error(f"Network error calling API: {e}")
        raise NetworkError("Unable to connect to Anthropic API. Check your internet connection.") from e
    except anthropic.RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        raise APIError("API rate limit exceeded. Please try again later.", 429) from e
    except anthropic.APIStatusError as e:
        logger.error(f"API error {e.status_code}: {e}")
        raise APIError(f"API request failed: {e.message}", e.status_code) from e
    except Exception as e:
        logger.error(f"Unexpected error calling API: {e}")
        raise APIError("Unexpected error during API call") from e
```

### Step 5: Main Function Error Handling

```python
def main():
    """Main entry point with comprehensive error handling."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Parse arguments
        args = parse_args()

        # Run main logic
        process_conversation(args)

    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileOperationError as e:
        print(f"File Error: {e}", file=sys.stderr)
        sys.exit(2)
    except NetworkError as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(3)
    except TTSError as e:
        print(f"Text-to-Speech Error: {e}", file=sys.stderr)
        sys.exit(4)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}", file=sys.stderr)
        print("Please report this issue with the full error log", file=sys.stderr)
        sys.exit(255)
```

## Acceptance Criteria

- [ ] All file operations have try/except blocks
- [ ] All network operations have error handling with retry logic
- [ ] Custom exception hierarchy is implemented
- [ ] User-friendly error messages (no stack traces in normal operation)
- [ ] Proper logging is configured
- [ ] Exit codes are meaningful and documented
- [ ] No sensitive information in error messages
- [ ] Graceful cleanup on errors (temp files removed)

## Testing

```python
def test_file_not_found():
    """Test handling of missing files."""
    with pytest.raises(FileOperationError, match="File not found"):
        parse_conversation("nonexistent.md")

def test_api_key_missing():
    """Test handling of missing API key."""
    with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}):
        with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
            generate_conversation("title", "content", "url")

def test_network_error_retry():
    """Test retry logic for network errors."""
    with patch('anthropic.Anthropic') as mock_client:
        mock_client.messages.create.side_effect = [
            anthropic.APIConnectionError("Network error"),
            anthropic.APIConnectionError("Network error"),
            MagicMock(content=[MagicMock(text="Success")])
        ]
        result = generate_conversation("title", "content", "url")
        assert result == "Success"
        assert mock_client.messages.create.call_count == 3
```

## References

- [Python Exception Handling Best Practices](https://docs.python.org/3/tutorial/errors.html)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Exit Codes With Special Meanings](https://tldp.org/LDP/abs/html/exitcodes.html)
