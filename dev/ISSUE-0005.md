# ISSUE-0005: Set Up Testing Infrastructure

**Priority**: CRITICAL  
**Type**: Testing & Quality Assurance  
**Effort**: 4-6 hours  

## Problem

The project currently has zero testing infrastructure:
- No unit tests
- No integration tests  
- No test fixtures or sample data
- No coverage reporting
- No test automation

This makes it impossible to verify code correctness, catch regressions, or confidently refactor code. For a public package, comprehensive testing is essential.

## Requirements

1. Set up pytest as the testing framework
2. Create test directory structure
3. Add unit tests for all modules (minimum 80% coverage)
4. Add integration tests for complete workflows
5. Create test fixtures and sample data
6. Configure coverage reporting
7. Add test automation (pre-commit hooks)

## Implementation Details

### Step 1: Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # pytest configuration
├── fixtures/                     # Test data
│   ├── sample_convo.md
│   ├── sample_html.html
│   └── test_audio.mp3
├── unit/                         # Unit tests
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_conversation_parser.py
│   ├── test_tts_edge.py
│   ├── test_tts_pyttsx3.py
│   └── test_url_fetcher.py
├── integration/                  # Integration tests
│   ├── __init__.py
│   ├── test_end_to_end.py
│   └── test_pipeline.py
└── performance/                  # Performance tests
    ├── __init__.py
    └── test_benchmarks.py
```

### Step 2: pytest Configuration

Create `tests/conftest.py`:
```python
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import os

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing."""
    return [
        ("ALEX", "Hello everyone, welcome to today's show."),
        ("JORDAN", "Thanks Alex! Today we're discussing the future of AI."),
        ("ALEX", "That's right. Let's dive into the key developments.")
    ]

@pytest.fixture
def sample_markdown():
    """Sample markdown conversation file content."""
    return """**ALEX:** Hello everyone, welcome to today's show.

**JORDAN:** Thanks Alex! Today we're discussing the future of AI.

**ALEX:** That's right. Let's dive into the key developments."""

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('anthropic.Anthropic') as mock:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated conversation")]
        mock_instance.messages.create.return_value = mock_response
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_edge_tts():
    """Mock edge-tts for testing."""
    with patch('edge_tts.Communicate') as mock:
        mock_instance = Mock()
        mock_instance.save = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def set_env_vars():
    """Set required environment variables for testing."""
    original_api_key = os.environ.get('ANTHROPIC_API_KEY')
    os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
    yield
    if original_api_key:
        os.environ['ANTHROPIC_API_KEY'] = original_api_key
    else:
        os.environ.pop('ANTHROPIC_API_KEY', None)
```

Create `pyproject.toml` for pytest configuration:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
    "--strict-markers",
    "-v"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
```

### Step 3: Unit Tests Examples

Create `tests/unit/test_validators.py`:
```python
import pytest
from src.convo.validators import (
    validate_url, validate_file_path, sanitize_html,
    validate_speaker_name, sanitize_text_for_tts,
    ValidationError
)

class TestURLValidation:
    def test_valid_https_url(self):
        url = "https://example.com/article"
        assert validate_url(url) == url
    
    def test_valid_http_url(self):
        url = "http://example.com/article"
        assert validate_url(url) == url
    
    def test_invalid_scheme(self):
        with pytest.raises(ValidationError, match="URL scheme must be"):
            validate_url("ftp://example.com")
    
    def test_no_scheme(self):
        with pytest.raises(ValidationError, match="must include scheme"):
            validate_url("example.com")
    
    def test_internal_ip_blocked(self):
        with pytest.raises(ValidationError, match="Internal URLs"):
            validate_url("http://192.168.1.1")
        
        with pytest.raises(ValidationError, match="Internal URLs"):
            validate_url("http://localhost:8080")

class TestSpeakerValidation:
    def test_valid_speaker_name(self):
        assert validate_speaker_name("ALEX") == "ALEX"
        assert validate_speaker_name("User_123") == "User_123"
    
    def test_invalid_characters(self):
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_speaker_name("ALEX'; DROP TABLE users; --")
    
    def test_too_long(self):
        long_name = "A" * 51
        with pytest.raises(ValidationError, match="too long"):
            validate_speaker_name(long_name)

class TestTextSanitization:
    def test_removes_dangerous_characters(self):
        dangerous = "Hello $USER `rm -rf /` world"
        safe = sanitize_text_for_tts(dangerous)
        assert "$" not in safe
        assert "`" not in safe
        assert "Hello" in safe
    
    def test_normalizes_whitespace(self):
        text = "Hello    world\n\n\ttest"
        result = sanitize_text_for_tts(text)
        assert result == "Hello world test"
    
    def test_limits_length(self):
        long_text = "A" * 6000
        result = sanitize_text_for_tts(long_text)
        assert len(result) <= 5003  # 5000 + "..."
        assert result.endswith("...")
```

Create `tests/unit/test_conversation_parser.py`:
```python
import pytest
from unittest.mock import mock_open, patch
from src.convo.parser import parse_conversation
from src.convo.exceptions import FileOperationError

class TestConversationParser:
    def test_parse_valid_conversation(self, temp_dir, sample_markdown):
        # Create test file
        test_file = temp_dir / "test.md"
        test_file.write_text(sample_markdown)
        
        result = parse_conversation(str(test_file))
        
        assert len(result) == 3
        assert result[0] == ("ALEX", "Hello everyone, welcome to today's show.")
        assert result[1] == ("JORDAN", "Thanks Alex! Today we're discussing the future of AI.")
    
    def test_file_not_found(self):
        with pytest.raises(FileOperationError, match="File not found"):
            parse_conversation("nonexistent.md")
    
    def test_empty_file(self, temp_dir):
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("")
        
        with pytest.raises(FileOperationError, match="File is empty"):
            parse_conversation(str(empty_file))
    
    @patch("builtins.open", mock_open(read_data="test"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_encoding_error(self):
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "error")):
            with pytest.raises(FileOperationError, match="encoding issue"):
                parse_conversation("test.md")
```

### Step 4: Integration Tests

Create `tests/integration/test_end_to_end.py`:
```python
import pytest
from unittest.mock import patch, Mock
import tempfile
import shutil
from pathlib import Path

@pytest.mark.integration
class TestEndToEndWorkflow:
    def test_url_to_audio_pipeline(self, mock_anthropic_client, mock_edge_tts, temp_dir):
        """Test complete pipeline from URL to audio."""
        # Mock web response
        mock_response = Mock()
        mock_response.text = "<html><title>Test Article</title><body>Test content</body></html>"
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            with patch('src.convo.url_fetcher.extract_content', return_value="Test content"):
                # Test the complete pipeline
                from src.convo.pipeline import process_url_to_audio
                
                result = process_url_to_audio(
                    url="https://example.com/article",
                    output_file=str(temp_dir / "output.mp3")
                )
                
                assert result is not None
                # Verify API was called
                mock_anthropic_client.messages.create.assert_called_once()
                # Verify TTS was called
                assert mock_edge_tts.called
    
    @pytest.mark.slow
    def test_large_conversation_processing(self, sample_conversation, temp_dir):
        """Test processing of large conversations."""
        # Create large conversation
        large_conversation = sample_conversation * 100
        
        # Test processing doesn't crash or timeout
        from src.convo.tts.edge import process_conversation
        
        with patch('edge_tts.Communicate') as mock_tts:
            mock_tts.return_value.save = Mock()
            
            result = process_conversation(
                large_conversation, 
                str(temp_dir / "large_output.mp3")
            )
            
            assert result is not None
```

### Step 5: Test Data Fixtures

Create `tests/fixtures/sample_convo.md`:
```markdown
**ALEX:** Welcome to Tech Talk Today. I'm Alex.

**JORDAN:** And I'm Jordan. Today we're exploring the latest developments in artificial intelligence.

**ALEX:** That's right, Jordan. AI has been making headlines with breakthrough discoveries in machine learning and natural language processing.

**JORDAN:** Absolutely. The recent advances in large language models have opened up new possibilities for human-computer interaction.
```

Create `tests/fixtures/sample_html.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Article: AI Breakthroughs</title>
</head>
<body>
    <article>
        <h1>AI Breakthroughs in 2024</h1>
        <p>This year has seen remarkable progress in artificial intelligence...</p>
        <p>Key developments include improved language models and computer vision systems.</p>
    </article>
</body>
</html>
```

### Step 6: Test Requirements

Create `requirements-test.txt`:
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
pytest-benchmark>=4.0.0
responses>=0.23.0
factory_boy>=3.3.0
```

### Step 7: Test Running Scripts

Create `scripts/run_tests.sh`:
```bash
#!/bin/bash
set -e

echo "Running unit tests..."
pytest tests/unit/ -v

echo "Running integration tests..."
pytest tests/integration/ -v -m "not slow"

echo "Running coverage report..."
pytest --cov=src --cov-report=html --cov-report=term-missing

echo "Running slow tests..."
pytest tests/ -v -k "slow" --timeout=300

echo "All tests completed!"
```

## Acceptance Criteria

- [ ] pytest framework is configured and working
- [ ] Test directory structure follows best practices
- [ ] Unit tests cover all modules with >80% coverage
- [ ] Integration tests verify complete workflows
- [ ] Test fixtures provide realistic sample data
- [ ] Coverage reporting is configured
- [ ] Tests can be run with simple commands
- [ ] CI/CD can run tests automatically
- [ ] Performance/benchmark tests are included

## Test Coverage Goals

- `validators.py`: 95% coverage
- `conversation_parser.py`: 90% coverage
- `tts/edge.py`: 85% coverage
- `tts/pyttsx3.py`: 85% coverage
- `url_fetcher.py`: 90% coverage
- Overall project: 80% minimum

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [Python Testing 101](https://realpython.com/python-testing/)
- [Test-Driven Development](https://testdriven.io/)