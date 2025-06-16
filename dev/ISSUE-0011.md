# ISSUE-0011: Set Up CI/CD Pipeline

**Priority**: MEDIUM  
**Type**: DevOps & Automation  
**Effort**: 3-4 hours  

## Problem

The project lacks automated testing and deployment:
- No continuous integration
- No automated testing on multiple Python versions
- No automated security scanning
- No automated releases
- No code quality checks in CI
- No deployment automation

This increases the risk of shipping bugs and makes maintenance difficult.

## Requirements

1. Set up GitHub Actions CI/CD pipeline
2. Test on multiple Python versions and platforms
3. Automated code quality checks (linting, formatting, type checking)
4. Security scanning in CI
5. Automated dependency updates
6. Automated releases to PyPI
7. Documentation building and deployment

## Implementation Details

### Step 1: Main CI Workflow

Create `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHONUNBUFFERED: 1
  FORCE_COLOR: 1

jobs:
  test:
    name: Test Python ${{ matrix.python-version }} on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
        exclude:
          # Exclude some combinations to reduce CI time
          - os: windows-latest
            python-version: "3.8"
          - os: macos-latest
            python-version: "3.8"
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y espeak espeak-data portaudio19-dev
    
    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        brew install espeak portaudio
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[all]
    
    - name: Run tests
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_TEST }}
      run: |
        pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      if: matrix.python-version == '3.11' && matrix.os == 'ubuntu-latest'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run black (code formatting)
      run: black --check --diff src/ tests/
    
    - name: Run isort (import sorting)
      run: isort --check-only --diff src/ tests/
    
    - name: Run flake8 (linting)
      run: flake8 src/ tests/
    
    - name: Run mypy (type checking)
      run: mypy src/
    
    - name: Run bandit (security linting)
      run: bandit -r src/ -f json > bandit-report.json || true
    
    - name: Upload bandit results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: bandit-report
        path: bandit-report.json

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run safety (dependency vulnerability scan)
      run: safety check --json > safety-report.json || true
    
    - name: Upload safety results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: safety-report
        path: safety-report.json
    
    - name: Run semgrep (SAST)
      uses: returntocorp/semgrep-action@v1
      with:
        config: auto
        generateSarif: "1"
    
    - name: Upload SARIF file
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: semgrep.sarif
      if: always()

  docs:
    name: Build Documentation
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[docs]
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Upload documentation
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: docs/build/html/

  integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [test, quality]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y espeak espeak-data portaudio19-dev
    
    - name: Install package
      run: |
        python -m pip install --upgrade pip
        pip install -e .[all]
    
    - name: Test CLI installation
      run: |
        convo --version
        convo --help
    
    - name: Test package import
      run: |
        python -c "import convo; print(f'✅ Package version: {convo.__version__}')"
    
    - name: Run integration tests
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_TEST }}
      run: |
        pytest tests/integration/ -v --timeout=300
```

### Step 2: Release Automation

Create `.github/workflows/release.yml`:
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

env:
  PYTHONUNBUFFERED: 1

jobs:
  build:
    name: Build Package
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  test-pypi:
    name: Test PyPI Upload
    runs-on: ubuntu-latest
    needs: build
    if: startsWith(github.ref, 'refs/tags/v') && contains(github.ref, '-')
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
    
    - name: Publish to Test PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.TEST_PYPI_API_TOKEN }}
        repository_url: https://test.pypi.org/legacy/

  pypi:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    needs: build
    if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, '-')
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}

  github-release:
    name: Create GitHub Release
    runs-on: ubuntu-latest
    needs: [build, pypi]
    if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, '-')
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
    
    - name: Extract release notes
      id: extract-release-notes
      run: |
        # Extract release notes from CHANGELOG.md
        python scripts/extract_changelog.py ${{ github.ref_name }} > release_notes.md
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*
        body_path: release_notes.md
        draft: false
        prerelease: ${{ contains(github.ref, '-') }}
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3: Documentation Deployment

Create `.github/workflows/docs.yml`:
```yaml
name: Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-docs:
    name: Build Documentation
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[docs]
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Upload to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: docs/build/html
        cname: convo.your-domain.com  # Optional: custom domain
```

### Step 4: Dependency Updates

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "maintainer-username"
    assignees:
      - "maintainer-username"
    commit-message:
      prefix: "deps"
      prefix-development: "deps-dev"
      include: "scope"
    groups:
      # Group development dependencies
      development:
        patterns:
          - "pytest*"
          - "black"
          - "isort"
          - "flake8*"
          - "mypy"
          - "bandit"
          - "safety"
      
      # Group documentation dependencies
      documentation:
        patterns:
          - "sphinx*"
          - "myst-parser"
      
      # Security updates (always separate)
      security:
        patterns:
          - "certifi"
          - "bleach"
        update-types:
          - "security"
  
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### Step 5: Pre-commit Configuration

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements
  
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings, flake8-type-checking]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--config-file=pyproject.toml]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]
  
  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.2
    hooks:
      - id: python-safety-dependencies-check
        files: pyproject.toml
```

### Step 6: Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.yml`:
```yaml
name: Bug Report
description: Report a bug to help us improve convo
title: "[BUG] "
labels: ["bug", "triage"]

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug! Please fill out the sections below.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: A clear description of what the bug is
      placeholder: Describe the bug...
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Run command '...'
        2. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What you expected to happen
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: |
        Please run the following commands and paste the output:
        - `convo --version`
        - `python --version`
        - `uname -a` (Linux/Mac) or `systeminfo` (Windows)
      render: shell
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Error Logs
      description: Any relevant error messages or logs
      render: shell

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Any other context about the problem
```

### Step 7: Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Other (please describe):

## Testing

- [ ] Tests pass locally
- [ ] New tests added for changed functionality
- [ ] Integration tests pass
- [ ] Documentation updated if needed

## Checklist

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Changelog updated (if applicable)

## Related Issues

Closes #(issue number)

## Screenshots (if applicable)

## Additional Notes

Any additional information about the changes.
```

### Step 8: Release Script

Create `scripts/extract_changelog.py`:
```python
#!/usr/bin/env python3
"""Extract release notes from CHANGELOG.md for GitHub releases."""

import sys
import re
from pathlib import Path

def extract_release_notes(version: str) -> str:
    """Extract release notes for a specific version from CHANGELOG.md."""
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    
    if not changelog_path.exists():
        return f"Release {version}"
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove 'v' prefix if present
    version = version.lstrip('v')
    
    # Pattern to match version sections
    pattern = rf"## \[{re.escape(version)}\].*?\n(.*?)(?=\n## \[|\n# |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return f"Release {version}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract_changelog.py <version>", file=sys.stderr)
        sys.exit(1)
    
    version = sys.argv[1]
    notes = extract_release_notes(version)
    print(notes)
```

## Acceptance Criteria

- [ ] CI pipeline runs on multiple Python versions and platforms
- [ ] Code quality checks (linting, formatting, type checking) run automatically
- [ ] Security scanning is integrated into CI
- [ ] Tests run automatically with coverage reporting
- [ ] Documentation builds automatically
- [ ] Releases are automated with proper versioning
- [ ] Dependencies are automatically updated
- [ ] Pre-commit hooks prevent bad commits
- [ ] Issue and PR templates guide contributors

## Setup Instructions

1. **Secrets Configuration**:
   ```bash
   # In GitHub repository settings > Secrets and variables > Actions
   PYPI_API_TOKEN=<your-pypi-token>
   TEST_PYPI_API_TOKEN=<your-test-pypi-token>
   ANTHROPIC_API_KEY_TEST=<test-api-key>
   ```

2. **Branch Protection**:
   - Require status checks to pass
   - Require up-to-date branches
   - Require review from code owners

3. **Enable GitHub Pages**:
   - Settings > Pages > Source: GitHub Actions

## Benefits

1. **Quality Assurance**: Automated testing prevents regressions
2. **Security**: Vulnerability scanning catches issues early
3. **Consistency**: Code formatting and linting maintain standards
4. **Efficiency**: Automated releases reduce manual work
5. **Documentation**: Always up-to-date docs
6. **Reliability**: Multi-platform testing ensures compatibility

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)