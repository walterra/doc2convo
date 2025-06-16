# ISSUE-0006: Restructure as Proper Python Package

**Priority**: CRITICAL  
**Type**: Package Structure & Distribution  
**Effort**: 3-4 hours  

## Problem

The current codebase is structured as loose scripts rather than a proper Python package:
- No `setup.py` or `pyproject.toml`
- Scripts in root directory instead of package structure
- No `__init__.py` files
- No version management
- Not installable via pip
- No entry points defined

This prevents proper distribution, dependency management, and integration with Python tooling.

## Requirements

1. Restructure code into proper Python package layout
2. Create `pyproject.toml` with modern packaging standards
3. Define entry points for CLI usage
4. Implement version management
5. Set up package metadata
6. Enable pip installation (local and PyPI)
7. Maintain backward compatibility during transition

## Implementation Details

### Step 1: New Package Structure

```
convo/
├── src/
│   └── convo/
│       ├── __init__.py              # Package init, version info
│       ├── cli.py                   # Command-line interfaces
│       ├── config.py                # Configuration management
│       ├── exceptions.py            # Custom exceptions
│       ├── validators.py            # Input validation
│       ├── tts/
│       │   ├── __init__.py
│       │   ├── base.py              # Base TTS class
│       │   ├── edge.py              # Edge TTS implementation
│       │   └── pyttsx3.py           # pyttsx3 implementation
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── parser.py            # Conversation parsing
│       │   └── processor.py         # Audio processing
│       └── web/
│           ├── __init__.py
│           ├── fetcher.py           # URL fetching
│           └── extractor.py         # Content extraction
├── tests/                           # Test suite (from ISSUE-0005)
├── docs/                            # Documentation
├── scripts/                         # Development scripts
├── pyproject.toml                   # Package configuration
├── README.md                        # Updated with installation
├── CHANGELOG.md                     # Version history
└── LICENSE                          # From ISSUE-0001
```

### Step 2: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "convo"
version = "0.1.0"
description = "Convert web articles and text to conversational audio podcasts"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.name@example.com"}
]
maintainers = [
    {name = "Your Name", email = "your.name@example.com"}
]
keywords = ["tts", "podcast", "audio", "conversation", "ai"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Sound/Audio :: Speech",
    "Topic :: Text Processing :: Markup :: HTML",
]
requires-python = ">=3.8"
dependencies = [
    "anthropic>=0.7.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "edge-tts>=6.1.0",
    "pyttsx3>=2.90",
    "pydub>=0.25.0",
    "click>=8.1.0",
    "rich>=13.0.0",
    "bleach>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.3.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
    "sphinx-click>=5.0.0",
]
all = ["convo[dev,docs]"]

[project.urls]
Homepage = "https://github.com/yourusername/convo"
Repository = "https://github.com/yourusername/convo.git"
Documentation = "https://convo.readthedocs.io/"
"Bug Reports" = "https://github.com/yourusername/convo/issues"
Changelog = "https://github.com/yourusername/convo/blob/main/CHANGELOG.md"

[project.scripts]
convo = "convo.cli:main"
convo-url = "convo.cli:url_to_audio"
convo-file = "convo.cli:file_to_audio"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
convo = ["py.typed"]

# Tool configurations
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

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
```

### Step 3: Create Package Init File

Create `src/convo/__init__.py`:
```python
"""Convo: Convert web articles to conversational audio podcasts."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.name@example.com"

from .exceptions import ConvoError, TTSError, NetworkError, APIError
from .tts import EdgeTTS, Pyttsx3TTS
from .converters import ConversationParser, AudioProcessor
from .web import URLFetcher, ContentExtractor

__all__ = [
    "ConvoError",
    "TTSError", 
    "NetworkError",
    "APIError",
    "EdgeTTS",
    "Pyttsx3TTS",
    "ConversationParser",
    "AudioProcessor",
    "URLFetcher",
    "ContentExtractor",
]
```

### Step 4: Create CLI Module

Create `src/convo/cli.py`:
```python
"""Command-line interface for convo package."""

import click
import sys
import logging
from pathlib import Path
from typing import Optional

from . import __version__
from .config import load_config
from .exceptions import ConvoError
from .tts import EdgeTTS, Pyttsx3TTS
from .converters import ConversationParser, AudioProcessor
from .web import URLFetcher, ContentExtractor

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def main(ctx, verbose: bool, config: Optional[str]):
    """Convert web articles and conversations to audio podcasts."""
    # Set up logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    ctx.obj['verbose'] = verbose

@main.command()
@click.argument('url')
@click.option('--output', '-o', default='podcast.mp3', help='Output audio file')
@click.option('--engine', '-e', 
              type=click.Choice(['edge', 'pyttsx3']), 
              default='edge',
              help='TTS engine to use')
@click.pass_context
def url(ctx, url: str, output: str, engine: str):
    """Convert web article to audio podcast."""
    try:
        click.echo(f"Fetching article from: {url}")
        
        # Fetch and extract content
        fetcher = URLFetcher()
        title, content = fetcher.fetch_article(url)
        
        # Generate conversation
        extractor = ContentExtractor()
        conversation = extractor.generate_conversation(title, content, url)
        
        # Convert to audio
        tts_engine = EdgeTTS() if engine == 'edge' else Pyttsx3TTS()
        processor = AudioProcessor(tts_engine)
        
        click.echo(f"Generating audio with {engine} engine...")
        processor.process_conversation(conversation, output)
        
        click.echo(f"✅ Audio saved to: {output}")
        
    except ConvoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(255)

@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='podcast.mp3', help='Output audio file')
@click.option('--engine', '-e', 
              type=click.Choice(['edge', 'pyttsx3']), 
              default='edge',
              help='TTS engine to use')
@click.pass_context
def file(ctx, file_path: str, output: str, engine: str):
    """Convert conversation file to audio podcast."""
    try:
        click.echo(f"Processing conversation file: {file_path}")
        
        # Parse conversation
        parser = ConversationParser()
        conversation = parser.parse_conversation(file_path)
        
        # Convert to audio
        tts_engine = EdgeTTS() if engine == 'edge' else Pyttsx3TTS()
        processor = AudioProcessor(tts_engine)
        
        click.echo(f"Generating audio with {engine} engine...")
        processor.process_conversation(conversation, output)
        
        click.echo(f"✅ Audio saved to: {output}")
        
    except ConvoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(255)

# Convenience functions for direct import
def url_to_audio():
    """Entry point for convo-url command."""
    main(['url'] + sys.argv[1:])

def file_to_audio():
    """Entry point for convo-file command."""
    main(['file'] + sys.argv[1:])

if __name__ == '__main__':
    main()
```

### Step 5: Migration Script

Create `scripts/migrate_to_package.py`:
```python
#!/usr/bin/env python3
"""Script to migrate existing code to new package structure."""

import shutil
import os
from pathlib import Path

def migrate_code():
    """Migrate existing code to new package structure."""
    root = Path(__file__).parent.parent
    src_dir = root / "src" / "convo"
    
    # Create directories
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "tts").mkdir(exist_ok=True)
    (src_dir / "converters").mkdir(exist_ok=True)
    (src_dir / "web").mkdir(exist_ok=True)
    
    # Mapping of old files to new locations
    migrations = {
        "edge_tts_converter.py": "tts/edge.py",
        "text_to_speech.py": "tts/pyttsx3.py",
        "url2convo.py": "web/fetcher.py",
        "url_to_convo.py": "web/extractor.py",
    }
    
    for old_file, new_path in migrations.items():
        old_path = root / old_file
        new_file = src_dir / new_path
        
        if old_path.exists():
            print(f"Migrating {old_file} -> {new_path}")
            shutil.copy2(old_path, new_file)
            
            # Create backup of original
            backup_dir = root / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.move(old_path, backup_dir / old_file)
    
    # Create __init__.py files
    init_files = [
        src_dir / "__init__.py",
        src_dir / "tts" / "__init__.py",
        src_dir / "converters" / "__init__.py", 
        src_dir / "web" / "__init__.py",
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.touch()
    
    print("Migration completed!")
    print("Next steps:")
    print("1. Update imports in migrated files")
    print("2. Test the new package structure")
    print("3. Install in development mode: pip install -e .")

if __name__ == "__main__":
    migrate_code()
```

### Step 6: Installation and Development

Create `scripts/dev_setup.sh`:
```bash
#!/bin/bash
set -e

echo "Setting up development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install package in development mode with all extras
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install

echo "Development environment set up successfully!"
echo "Activate with: source venv/bin/activate"
echo "Run tests with: pytest"
echo "Build package with: python -m build"
```

## Acceptance Criteria

- [ ] Code is restructured into proper Python package layout
- [ ] `pyproject.toml` is configured with all metadata
- [ ] Package can be installed with `pip install -e .`
- [ ] CLI commands work: `convo url <url>` and `convo file <file>`
- [ ] Entry points are properly defined
- [ ] Version management is implemented
- [ ] All imports are updated to use new structure
- [ ] Backward compatibility is maintained
- [ ] Package can be built for PyPI distribution

## Testing

```bash
# Test local installation
pip install -e .

# Test CLI commands
convo --help
convo url --help
convo file --help

# Test package import
python -c "import convo; print(convo.__version__)"

# Test building for distribution
python -m build
```

## Migration Checklist

- [ ] Run migration script
- [ ] Update all imports in source files
- [ ] Update configuration files
- [ ] Update documentation
- [ ] Test CLI functionality
- [ ] Test package installation
- [ ] Update CI/CD to use new structure
- [ ] Create release workflow

## References

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [Click CLI Framework](https://click.palletsprojects.com/)