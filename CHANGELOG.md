# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial implementation of doc2convo toolkit
- URL-to-conversation conversion using Claude AI (`doc2md-convo`)
- Text-to-speech conversion using Edge TTS (`md-convo2mp3`)
- Two-speaker podcast format (ALEX and JORDAN)
- Support for web content extraction and cleaning with BeautifulSoup
- Local file support for .txt, .md, and .pdf files
- Piping support between doc2md-convo and md-convo2mp3
- Randomized speaker role assignment to avoid gender bias
- MIT license implementation with header enforcement
- Code linting and formatting standards
- Development issue tracking system in `dev/` directory
- Comprehensive CLAUDE.md development guidelines
- Configurable speech speed (25% faster for natural flow)
- Automatic temporary file cleanup
- Support for custom system prompts
- Proper Python package structure under `src/doc2convo/`
- Package metadata and dependencies in `pyproject.toml`
- CLI entry points for installed commands

### Changed

- Renamed `url2convo.py` to `doc2md-convo.py` for clarity
- Renamed `edge_tts_converter.py` to `md-convo2mp3.py` for consistency
- Improved conversation prompts and generation quality
- Consolidated requirements management
- Restructured as installable Python package

### Fixed

- Command injection vulnerability in temporary file handling
- Enhanced security in file processing pipeline
- Fixed two-speaker voice mapping

### Removed

- Removed fallback `say` command functionality
- Removed deprecated `text_to_speech.py` module
- Removed dummy TTS engine
- Removed standalone `doc2md-convo.py` and `md-convo2mp3.py` scripts (replaced by package entry points)
