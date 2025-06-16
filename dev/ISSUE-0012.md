# ISSUE-0012: Add Development Tooling and Environment

**Priority**: LOW  
**Type**: Developer Experience  
**Effort**: 2-3 hours  

## Problem

The project lacks modern development tooling:
- No pre-commit hooks configured
- No linting configuration files
- No code formatting automation
- No development environment setup script
- No editor configuration
- No debugging configuration

This makes development inconsistent and error-prone.

## Requirements

1. Set up comprehensive pre-commit hooks
2. Configure linting and formatting tools
3. Add editor configuration (VS Code, PyCharm)
4. Create development environment setup scripts
5. Add debugging configurations
6. Set up profiling and performance tools
7. Add development documentation

## Implementation Details

### Step 1: Pre-commit Configuration

Already covered in ISSUE-0011, but here's the expanded version:

Create `.pre-commit-config.yaml`:
```yaml
repos:
  # Basic hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-toml
      - id: check-json
      - id: debug-statements
      - id: name-tests-test
        args: ['--django']
      - id: requirements-txt-fixer

  # Python code formatting
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]

  # Import sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black", "--line-length=88"]

  # Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        additional_dependencies: 
          - flake8-docstrings
          - flake8-type-checking
          - flake8-bugbear
          - flake8-comprehensions
          - flake8-simplify

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--config-file=pyproject.toml]
        exclude: tests/

  # Security
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  # Dependency security
  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.2
    hooks:
      - id: python-safety-dependencies-check
        files: pyproject.toml

  # Documentation
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: [--convention=google]

  # Spell checking
  - repo: https://github.com/crate-ci/typos
    rev: v1.16.20
    hooks:
      - id: typos

  # Commit message formatting
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [optional-scope]

  # Upgrade syntax
  - repo: https://github.com/asottile/pyupgrade
    rev: v3.15.0
    hooks:
      - id: pyupgrade
        args: [--py38-plus]

  # Remove unused imports and variables
  - repo: https://github.com/PyCQA/autoflake
    rev: v2.2.1
    hooks:
      - id: autoflake
        args:
          - --in-place
          - --remove-all-unused-imports
          - --remove-unused-variables
          - --remove-duplicate-keys
          - --ignore-init-module-imports
```

### Step 2: Tool Configuration in pyproject.toml

Add comprehensive tool configuration:

```toml
# Black configuration
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

# isort configuration
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["convo"]
known_third_party = ["pytest", "anthropic", "edge_tts", "pyttsx3"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

# flake8 configuration
[tool.flake8]
max-line-length = 88
extend-ignore = [
    "E203",  # whitespace before ':'
    "E501",  # line too long (handled by black)
    "W503",  # line break before binary operator
]
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".venv",
    ".eggs",
    "*.egg",
]
per-file-ignores = [
    "__init__.py:F401",  # unused imports in __init__.py
    "tests/*:D",  # no docstrings in tests
]

# mypy configuration
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
    "bs4.*",
]
ignore_missing_imports = true

# bandit configuration
[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # assert_used

# coverage configuration
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

# pydocstyle configuration
[tool.pydocstyle]
convention = "google"
add_ignore = ["D100", "D104", "D105", "D107"]  # Missing docstrings
match_dir = "src"

# pytest configuration (enhanced)
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--cov-fail-under=80",
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "security: marks tests as security-related",
    "performance: marks tests as performance benchmarks",
]
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

### Step 3: Editor Configuration

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true,
    "[python]": {
        "editor.rulers": [88],
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    },
    "[yaml]": {
        "editor.tabSize": 2,
        "editor.insertSpaces": true
    },
    "[json]": {
        "editor.tabSize": 2,
        "editor.insertSpaces": true
    }
}
```

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Python: CLI - URL to Audio",
            "type": "python",
            "request": "launch",
            "module": "convo.cli",
            "args": ["url", "https://example.com/article", "-o", "test.mp3"],
            "console": "integratedTerminal",
            "env": {
                "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"
            }
        },
        {
            "name": "Python: CLI - File to Audio",
            "type": "python",
            "request": "launch",
            "module": "convo.cli",
            "args": ["file", "tests/fixtures/sample_convo.md", "-o", "test.mp3"],
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Test Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v"],
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Python: Test with Coverage",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["--cov=src", "--cov-report=html", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

Create `.vscode/extensions.json`:
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "ms-python.black-formatter",
        "ms-python.isort",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-json",
        "github.vscode-github-actions",
        "github.copilot",
        "tamasfe.even-better-toml"
    ]
}
```

### Step 4: Development Scripts

Create `scripts/dev_setup.sh`:
```bash
#!/bin/bash
set -e

echo "🔧 Setting up development environment for Convo..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📍 Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8+ required"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package with all extras
echo "📦 Installing package in development mode..."
pip install -e ".[all]"

# Install additional development tools
echo "🛠️  Installing additional development tools..."
pip install \
    pre-commit \
    tox \
    pip-tools \
    pip-licenses \
    interrogate

# Set up pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p .vscode logs temp

# Set up git hooks (if git repo)
if [ -d ".git" ]; then
    echo "📋 Setting up git configuration..."
    git config --local core.autocrlf false
    git config --local core.eol lf
fi

# Test installation
echo "🧪 Testing installation..."
python -c "import convo; print(f'✅ Convo {convo.__version__} installed successfully')"

# Run pre-commit on all files
echo "🔍 Running pre-commit on all files..."
pre-commit run --all-files || echo "⚠️  Some pre-commit checks failed - this is normal for first setup"

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run tests: pytest"
echo "  3. Check code quality: pre-commit run --all-files"
echo "  4. Build docs: cd docs && make html"
echo ""
echo "Useful commands:"
echo "  - Run specific tests: pytest tests/test_validators.py -v"
echo "  - Format code: black src/ tests/"
echo "  - Type check: mypy src/"
echo "  - Security scan: bandit -r src/"
echo "  - Dependency check: safety check"
```

Create `scripts/quality_check.sh`:
```bash
#!/bin/bash
set -e

echo "🔍 Running comprehensive quality checks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "📊 Code formatting check..."
black --check --diff src/ tests/ || {
    echo "❌ Code formatting issues found. Run: black src/ tests/"
    exit 1
}

echo "📋 Import sorting check..."
isort --check-only --diff src/ tests/ || {
    echo "❌ Import sorting issues found. Run: isort src/ tests/"
    exit 1
}

echo "🔧 Linting check..."
flake8 src/ tests/ || {
    echo "❌ Linting issues found"
    exit 1
}

echo "🔍 Type checking..."
mypy src/ || {
    echo "❌ Type checking issues found"
    exit 1
}

echo "🔒 Security scanning..."
bandit -r src/ || {
    echo "❌ Security issues found"
    exit 1
}

echo "🛡️  Dependency vulnerability check..."
safety check || {
    echo "❌ Vulnerable dependencies found"
    exit 1
}

echo "📝 Documentation style check..."
pydocstyle src/ || {
    echo "❌ Documentation style issues found"
    exit 1
}

echo "🧪 Running tests..."
pytest tests/ --cov=src --cov-fail-under=80 || {
    echo "❌ Tests failed or coverage below 80%"
    exit 1
}

echo "✅ All quality checks passed!"
```

Create `scripts/clean.sh`:
```bash
#!/bin/bash

echo "🧹 Cleaning up development artifacts..."

# Remove Python cache
find . -type d -name "__pycache__" -delete 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove build artifacts
rm -rf build/ dist/ .eggs/ || true

# Remove test artifacts
rm -rf .pytest_cache/ .coverage htmlcov/ coverage.xml || true

# Remove mypy cache
rm -rf .mypy_cache/ || true

# Remove tox cache
rm -rf .tox/ || true

# Remove temporary files
rm -rf temp/ logs/*.log || true

echo "✅ Cleanup complete!"
```

### Step 5: Performance and Profiling Tools

Create `scripts/profile.py`:
```python
#!/usr/bin/env python3
"""Performance profiling utilities for convo."""

import cProfile
import pstats
import time
from pathlib import Path
from typing import Any, Callable
import memory_profiler

def profile_function(func: Callable, *args, **kwargs) -> Any:
    """Profile a function's execution time and memory usage."""
    print(f"🔍 Profiling function: {func.__name__}")
    
    # Time profiling
    pr = cProfile.Profile()
    pr.enable()
    
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    pr.disable()
    
    # Save and display results
    stats_file = Path(f"profile_{func.__name__}_{int(time.time())}.prof")
    pr.dump_stats(str(stats_file))
    
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    print(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")
    print(f"📊 Profile saved to: {stats_file}")
    
    return result

@memory_profiler.profile
def profile_memory(func: Callable, *args, **kwargs) -> Any:
    """Profile memory usage of a function."""
    return func(*args, **kwargs)

if __name__ == "__main__":
    # Example usage
    from convo.converters.parser import parse_conversation
    
    # Profile conversation parsing
    sample_file = "tests/fixtures/sample_convo.md"
    if Path(sample_file).exists():
        profile_function(parse_conversation, sample_file)
    else:
        print(f"Sample file not found: {sample_file}")
```

### Step 6: Makefile for Common Tasks

Create `Makefile`:
```makefile
.PHONY: help install dev-setup test lint format type-check security docs clean build release

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package for production
	pip install .

dev-setup: ## Set up development environment
	./scripts/dev_setup.sh

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting
	flake8 src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

type-check: ## Run type checking
	mypy src/

security: ## Run security checks
	bandit -r src/
	safety check

quality: ## Run all quality checks
	./scripts/quality_check.sh

docs: ## Build documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs/build/html && python -m http.server 8000

clean: ## Clean up build artifacts
	./scripts/clean.sh

build: ## Build package
	python -m build

profile: ## Profile performance
	python scripts/profile.py

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

release-test: ## Release to Test PyPI
	python -m build
	twine check dist/*
	twine upload --repository testpypi dist/*

release: ## Release to PyPI
	python -m build
	twine check dist/*
	twine upload dist/*

dev: ## Start development server/watcher
	python -m convo.cli --help

update-deps: ## Update all dependencies
	pip-compile --upgrade pyproject.toml
	pip install -e .[all]

check-licenses: ## Check dependency licenses
	pip-licenses --format=table

all: format lint type-check security test ## Run all checks
```

### Step 7: Editor Configuration for All Editors

Create `.editorconfig`:
```ini
# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{yml,yaml}]
indent_style = space
indent_size = 2

[*.{json,toml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

## Acceptance Criteria

- [ ] Pre-commit hooks are configured and working
- [ ] All linting and formatting tools are configured consistently
- [ ] Development environment setup is automated
- [ ] Editor configurations work for common editors
- [ ] Quality checking scripts run all necessary checks
- [ ] Performance profiling tools are available
- [ ] Makefile provides convenient command interface
- [ ] Development documentation explains the tooling

## Usage Instructions

```bash
# Initial setup
./scripts/dev_setup.sh

# Daily development workflow
make format      # Format code
make lint        # Check linting
make type-check  # Type checking
make test        # Run tests
make quality     # All quality checks

# Before committing (automatic via pre-commit hooks)
make all

# Build and release
make build
make release-test  # Test release
make release       # Production release
```

## Benefits

1. **Consistency**: All developers use the same tools and configurations
2. **Quality**: Automated checks prevent low-quality code
3. **Efficiency**: Scripts automate repetitive tasks
4. **Documentation**: Clear commands and help text
5. **Onboarding**: New developers can get started quickly
6. **Maintainability**: Consistent code style and structure

## References

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [VS Code Python Development](https://code.visualstudio.com/docs/python/python-tutorial)
- [EditorConfig](https://editorconfig.org/)