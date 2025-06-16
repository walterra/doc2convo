# ISSUE-0002: Fix Command Injection Vulnerability in edge_tts_converter.py

**Priority**: CRITICAL  
**Type**: Security Vulnerability  
**Effort**: 30 minutes  
**Severity**: HIGH - Remote Code Execution Risk

## Problem

The file `edge_tts_converter.py` lines 23-25 uses `os.system()` to remove temporary files:

```python
os.system("rm -rf temp_audio_files")
```

This is vulnerable to command injection if the directory name is ever made configurable. Additionally, using shell commands for file operations is bad practice and not cross-platform compatible.

## Security Risk

- If directory names become user-configurable, attackers could inject commands
- Shell execution is inherently risky
- Current implementation won't work on Windows

## Requirements

1. Replace all `os.system()` calls with secure Python equivalents
2. Use proper temporary directory handling
3. Ensure cross-platform compatibility
4. No shell command execution for file operations

## Implementation Details

### Current Vulnerable Code
```python
# Line 23-25 in edge_tts_converter.py
os.system("rm -rf temp_audio_files")
os.makedirs("temp_audio_files", exist_ok=True)
```

### Secure Replacement

Option 1: Use tempfile module (Recommended)
```python
import tempfile
import shutil
from pathlib import Path

# Create secure temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    
    # Do work with temp files
    for i, (speaker, text) in enumerate(conversation):
        output_file = temp_path / f"part_{i}.mp3"
        # ... rest of processing
    
    # Combine files
    # ... 
    
# Directory automatically cleaned up when context exits
```

Option 2: Manual secure cleanup
```python
import shutil
from pathlib import Path

# Remove directory safely
temp_dir = Path("temp_audio_files")
if temp_dir.exists() and temp_dir.is_dir():
    shutil.rmtree(temp_dir)

# Create directory
temp_dir.mkdir(exist_ok=True)
```

### Additional Security Hardening

1. Never construct file paths from user input without validation
2. Use pathlib for all path operations
3. Validate all file operations stay within expected directories

## Acceptance Criteria

- [ ] No `os.system()` calls remain in the codebase
- [ ] All file operations use Python's built-in modules
- [ ] Temporary files are properly cleaned up
- [ ] Code works on Windows, macOS, and Linux
- [ ] No shell commands are executed

## Testing

```python
# Test secure temp directory handling
def test_temp_directory_cleanup():
    """Ensure temp directories are cleaned up properly."""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "test.txt")
        with open(temp_file, 'w') as f:
            f.write("test")
        assert os.path.exists(temp_file)
    
    # Directory should be gone after context
    assert not os.path.exists(temp_dir)
```

## References

- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- [Python tempfile documentation](https://docs.python.org/3/library/tempfile.html)
- [Python shutil documentation](https://docs.python.org/3/library/shutil.html)
- [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)