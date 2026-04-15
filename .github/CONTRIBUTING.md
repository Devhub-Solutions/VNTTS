# Contributing to VNTTS

Thank you for your interest in contributing to VNTTS! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/VNTTS.git
cd VNTTS

# Add upstream remote
git remote add upstream https://github.com/Devhub-Solutions/VNTTS.git
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install additional dev tools
pip install black isort pylint pyright pytest-cov
```

## Development Workflow

### 1. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make changes

- Write clean, readable code
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Include type hints where possible

### 3. Format & Lint

```bash
# Auto-format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check types
pyright src/

# Lint
pylint src/vntts --disable=all --enable=E,F,W
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/vntts

# Run specific test
pytest tests/test_tts.py::TestTTSInit -v
```

### 5. Commit & Push

```bash
# Commit with meaningful message
git commit -m "feat: add new TTS feature" -m "Description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub and create PR against `main`
- Describe what changed and why
- Reference any related issues (#123)
- Wait for CI checks to pass
- Address review comments

## File Structure

```
VNTTS/
├── src/vntts/              # Source code
│   ├── __init__.py         # Package init
│   ├── tts.py              # TTS class
│   ├── stt.py              # STT class
│   └── model_parts.py      # Model splitting/merging
├── tests/                  # Unit tests
│   ├── test_tts.py
│   ├── test_stt.py
│   └── test_model_parts.py
├── models/                 # Model files (split)
│   ├── banmai/            # TTS model parts
│   └── asr/               # ASR model parts
├── scripts/               # Utility scripts
│   ├── split_model.py
│   └── merge_model.py
├── .github/workflows/     # CI/CD workflows
├── pyproject.toml         # Project metadata
└── README.md              # Documentation
```

## Coding Standards

### Python Style

```python
# Type hints
def process_text(text: str) -> str:
    """Process Vietnamese text."""
    return text.strip()

# Docstrings
def recognize(file_path: str | Path) -> str:
    """
    Recognize speech from audio file.
    
    Parameters
    ----------
    file_path : str | Path
        Path to WAV audio file
        
    Returns
    -------
    str
        Recognized text
    """
    ...

# Constants in UPPER_CASE
SAMPLE_RATE = 22050
DEFAULT_CHUNK_SIZE = 80 * 1024 * 1024
```

### Git Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Test additions
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `chore:` Maintenance

Example:
```
feat: add GPU support for TTS inference

- Add use_cuda parameter to TTS class
- Update documentation
- Add related tests
```

## Testing

### Writing Tests

```python
import pytest
from vntts import TTS

class TestMyFeature:
    def setup_method(self):
        """Setup for each test."""
        self.tts = TTS()
    
    def test_feature_works(self):
        """Test the feature."""
        result = self.tts.speak("test")
        assert result is not None
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            self.tts.speak(None)
```

### Test Organization

- One test file per module
- Group tests in classes
- Use descriptive test names
- Test both success and failure cases
- Include docstrings

## Model Updates

For adding/updating models:

1. Download model to appropriate directory
2. Split if needed: `python scripts/split_model.py <file> --write-checksum`
3. Remove original large file
4. Update `models/README.md` with details
5. Test locally before PR
6. Commit `.part*` files and metadata

## Documentation

- Update README.md for user-facing changes
- Keep docstrings in sync with code
- Add examples for new features
- Document breaking changes

## Release Process

See [RELEASE.md](../RELEASE.md) for:
- PyPI publication process
- Version management
- Release checklist

## Reporting Issues

When reporting bugs:
1. Check existing issues first
2. Include Python version: `python --version`
3. Provide minimal reproduction code
4. Describe expected vs actual behavior
5. Include error traceback

## Suggesting Features

- Describe the feature clearly
- Explain the use case
- Provide examples if possible
- Link related issues/discussions

## Questions?

- Open a discussion on GitHub
- Check existing documentation
- Review test examples for usage patterns

## License

By contributing, you agree your code will be licensed under MIT License.

Thank you for contributing! 🙏
