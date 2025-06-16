# ISSUE-0008: Consolidate and Pin Dependencies

**Priority**: MEDIUM  
**Type**: Dependency Management  
**Effort**: 1-2 hours  

## Problem

The current project has confusing dependency management:
- Three separate requirements files (`requirements.txt`, `requirements-edge.txt`, `requirements-claude.txt`)
- No version pinning for dependencies
- Missing optional dependency documentation
- No dependency conflict resolution
- No security vulnerability scanning

This makes installation unreliable and creates potential security risks.

## Requirements

1. Consolidate all dependencies into pyproject.toml
2. Pin versions with compatible ranges
3. Organize dependencies by purpose (core, dev, docs, etc.)
4. Add security scanning for vulnerabilities
5. Document dependency choices and alternatives
6. Set up dependency update automation

## Implementation Details

### Step 1: Audit Current Dependencies

Current dependencies found:
- `requirements.txt`: pyttsx3, beautifulsoup4, requests
- `requirements-edge.txt`: edge-tts, pydub, anthropic, beautifulsoup4, requests  
- `requirements-claude.txt`: anthropic

### Step 2: Consolidate in pyproject.toml

Update `pyproject.toml`:
```toml
[project]
name = "convo"
dependencies = [
    # Core web scraping
    "beautifulsoup4>=4.12.0,<5.0.0",
    "requests>=2.31.0,<3.0.0",
    "lxml>=4.9.0,<6.0.0",  # Better HTML parsing
    
    # AI/LLM
    "anthropic>=0.7.0,<1.0.0",
    
    # Audio processing (core)
    "pydub>=0.25.0,<1.0.0",
    
    # CLI and utilities
    "click>=8.1.0,<9.0.0",
    "rich>=13.0.0,<14.0.0",  # Better terminal output
    "pydantic>=2.0.0,<3.0.0",  # Configuration validation
    
    # Security
    "bleach>=6.0.0,<7.0.0",  # HTML sanitization
    "certifi>=2023.7.22",  # Updated certificates
]

[project.optional-dependencies]
# TTS engines (user chooses one or both)
edge-tts = [
    "edge-tts>=6.1.0,<7.0.0",
]
pyttsx3 = [
    "pyttsx3>=2.90,<3.0.0",
]

# Development dependencies  
dev = [
    # Testing
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-mock>=3.11.0,<4.0.0",
    "pytest-asyncio>=0.21.0,<1.0.0",
    "pytest-benchmark>=4.0.0,<5.0.0",
    "responses>=0.23.0,<1.0.0",
    
    # Code quality
    "black>=23.0.0,<25.0.0",
    "isort>=5.12.0,<6.0.0", 
    "flake8>=6.0.0,<8.0.0",
    "flake8-docstrings>=1.7.0,<2.0.0",
    "flake8-type-checking>=2.4.0,<3.0.0",
    
    # Type checking
    "mypy>=1.5.0,<2.0.0",
    "types-requests>=2.31.0",
    "types-beautifulsoup4>=4.12.0",
    
    # Security scanning
    "bandit>=1.7.0,<2.0.0",
    "safety>=2.3.0,<4.0.0",
    
    # Development tools
    "pre-commit>=3.3.0,<4.0.0",
    "tox>=4.0.0,<5.0.0",
]

# Documentation dependencies
docs = [
    "sphinx>=7.0.0,<8.0.0",
    "sphinx-rtd-theme>=1.3.0,<2.0.0",
    "sphinx-click>=5.0.0,<6.0.0",
    "sphinx-autodoc-typehints>=1.24.0,<2.0.0",
    "myst-parser>=2.0.0,<3.0.0",  # Markdown support
]

# Performance profiling
profile = [
    "py-spy>=0.3.14,<1.0.0",
    "memory-profiler>=0.61.0,<1.0.0",
]

# All extras for comprehensive development
all = [
    "convo[edge-tts,pyttsx3,dev,docs,profile]"
]

# Minimal installation (no TTS engines)
minimal = []
```

### Step 3: Create Dependency Documentation

Create `docs/dependencies.md`:
```markdown
# Dependency Guide

## Core Dependencies

### Web Scraping
- **beautifulsoup4**: HTML parsing and content extraction
- **requests**: HTTP client for fetching web content  
- **lxml**: Fast XML/HTML parser (optional but recommended)

### AI/LLM
- **anthropic**: Claude API client for conversation generation

### Audio Processing
- **pydub**: Audio manipulation and format conversion

### CLI and UI
- **click**: Command-line interface framework
- **rich**: Enhanced terminal output with colors and formatting

### Configuration
- **pydantic**: Data validation and settings management

### Security
- **bleach**: HTML sanitization to prevent XSS
- **certifi**: Up-to-date SSL certificates

## Optional Dependencies

### TTS Engines (Choose One or Both)

#### Edge TTS (Recommended)
```bash
pip install convo[edge-tts]
```
- **edge-tts**: Microsoft Edge neural voices (online)
- Pros: High quality, many voices, no setup
- Cons: Requires internet connection

#### pyttsx3 (Offline)
```bash  
pip install convo[pyttsx3]
```
- **pyttsx3**: System TTS interface (offline)
- Pros: Works offline, system voices
- Cons: Quality varies by OS, limited voices

#### Both Engines
```bash
pip install convo[edge-tts,pyttsx3]
```

## Development Dependencies

Install development environment:
```bash
pip install convo[dev]
```

Includes:
- Testing framework (pytest + plugins)
- Code formatting (black, isort)
- Linting (flake8 + plugins)  
- Type checking (mypy + stubs)
- Security scanning (bandit, safety)
- Pre-commit hooks

## Documentation Dependencies

For building documentation:
```bash
pip install convo[docs]
```

## Installation Examples

```bash
# Minimal installation (no TTS)
pip install convo

# Production with Edge TTS
pip install convo[edge-tts]

# Development setup
pip install convo[all]

# Custom combination
pip install convo[edge-tts,docs]
```

## Version Pinning Strategy

- **Core dependencies**: Pin major version, allow minor updates
- **Development tools**: Allow broader ranges for compatibility
- **Security-critical**: Pin to specific secure versions
- **Optional**: User choice, minimal constraints

## Security Considerations

Dependencies are scanned for vulnerabilities using:
- `safety check` for known vulnerabilities
- `bandit` for security anti-patterns
- Regular updates via Dependabot

## Alternatives Considered

| Dependency | Alternative | Why Not Chosen |
|------------|-------------|----------------|
| requests | httpx | Requests is more stable/mature |
| click | argparse | Click provides better UX |
| pydub | librosa | Pydub is simpler for basic tasks |
| anthropic | openai | Project specifically uses Claude |
```

### Step 4: Security Scanning Configuration

Create `.bandit`:
```ini
[bandit]
# Skip tests directory  
exclude_dirs = ["tests"]

# Skip specific checks that are false positives
skips = ["B101"]  # Skip assert_used test

[bandit.assert_used]
skips = ["**/test_*.py", "**/tests.py"]
```

Create `pyproject.toml` safety config:
```toml
[tool.safety]
# Ignore specific vulnerabilities if needed
# ignore = ["39462", "40291"]

[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]
```

### Step 5: Dependency Update Automation

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "maintainer-username"
    commit-message:
      prefix: "deps"
      include: "scope"
    groups:
      development:
        patterns:
          - "pytest*"
          - "black"
          - "isort"
          - "flake8*"
          - "mypy"
        
      security:
        patterns:
          - "bandit"
          - "safety"
          - "certifi"
          - "bleach"
        update-types:
          - "security"
```

### Step 6: Scripts for Dependency Management

Create `scripts/check_deps.py`:
```python
#!/usr/bin/env python3
"""Script to check and update dependencies."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str]) -> bool:
    """Run command and return success status."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {' '.join(cmd)}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    """Check dependencies for security issues and updates."""
    print("🔍 Checking dependencies...")
    
    # Security checks
    print("\n📊 Security scanning...")
    safety_ok = run_command(["safety", "check"])
    bandit_ok = run_command(["bandit", "-r", "src/"])
    
    # Dependency analysis
    print("\n📦 Analyzing dependencies...")
    run_command(["pip", "list", "--outdated"])
    
    # License check (if pipdeptree is installed)
    try:
        run_command(["pip-licenses", "--format=table"])
    except FileNotFoundError:
        print("💡 Install pip-licenses for license analysis: pip install pip-licenses")
    
    if not (safety_ok and bandit_ok):
        print("\n⚠️  Security issues found!")
        sys.exit(1)
    else:
        print("\n✅ All security checks passed!")

if __name__ == "__main__":
    main()
```

Create `scripts/update_deps.sh`:
```bash
#!/bin/bash
set -e

echo "🔄 Updating dependencies..."

# Update pip itself
pip install --upgrade pip

# Check for security vulnerabilities first
echo "🔒 Checking for security issues..."
safety check || echo "⚠️  Security issues found - review before updating"

# Update all dependencies
echo "📦 Updating packages..."
pip install --upgrade --upgrade-strategy eager -e .[all]

# Run tests to ensure updates don't break anything
echo "🧪 Running tests after update..."
pytest tests/ -v

echo "✅ Dependencies updated successfully!"
```

## Acceptance Criteria

- [ ] All dependencies consolidated in pyproject.toml
- [ ] Version ranges are appropriately pinned
- [ ] Optional dependencies are clearly organized
- [ ] Security scanning is configured and working
- [ ] Documentation explains dependency choices
- [ ] Automated dependency updates are configured
- [ ] Installation works with different dependency combinations
- [ ] No dependency conflicts in any configuration

## Testing

```bash
# Test minimal installation
pip install .

# Test with different optional dependencies
pip install .[edge-tts]
pip install .[pyttsx3]
pip install .[dev]

# Test security scanning
bandit -r src/
safety check

# Test dependency resolution
pip-compile --resolver=backtracking pyproject.toml
```

## Migration from Current Requirements Files

```bash
# Backup old files
mkdir backup
mv requirements*.txt backup/

# Install from new configuration
pip install -e .[all]

# Verify everything works
python -c "import convo; print('✅ Import successful')"
convo --help
```

## References

- [Python Packaging Dependencies](https://packaging.python.org/guides/writing-pyproject-toml/)
- [pip-tools for dependency management](https://pip-tools.readthedocs.io/)
- [Safety for vulnerability scanning](https://pyup.io/safety/)
- [Bandit security linter](https://bandit.readthedocs.io/)