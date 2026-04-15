# Release and Deployment Guide

## Setting up PyPI Publishing

### 1. Create PyPI API Token

1. Go to https://pypi.org/account/ and log in
2. Navigate to "API tokens" in your account settings
3. Create a new API token with scope "Entire account"
4. Copy the token (format: `pypi-....`)

### 2. Add Secret to GitHub

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the token from PyPI
6. Click "Add secret"

### 3. Create a Release

#### Automatic Publishing 
The workflow is triggered when you create a GitHub release:

```bash
# 1. Update version in pyproject.toml
# Edit version = "0.1.0" to version = "0.2.0"

# 2. Commit and push
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main

# 3. Create GitHub release via CLI
gh release create v0.2.0 --generate-notes

# Or create via GitHub web interface:
# - Go to Releases → "Create a new release"
# - Tag name: v0.2.0
# - Release title: Version 0.2.0
# - Generate release notes
# - Publish release
```

#### Manual Trigger (without creating a release)

Go to: **Actions** → **Publish to PyPI** → **Run workflow** → **main branch**

### 4. Verify Publication

After workflow completes:

```bash
pip install --upgrade vntts
pip show vntts  # Check version
```

Or check: https://pypi.org/project/vntts/

## Version Management

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 0.2.1)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Update in `pyproject.toml`:
```toml
version = "0.2.1"
```

## Release Checklist

- [ ] Update `pyproject.toml` version
- [ ] Update `CHANGELOG.md` (optional but recommended)
- [ ] Commit with message like "Bump version to X.Y.Z"
- [ ] Push to main
- [ ] Create GitHub release with tag vX.Y.Z
- [ ] Verify publication on PyPI (may take a few minutes)
- [ ] Test: `pip install --upgrade vntts`

## Troubleshooting

### Publish Workflow Failed

Check GitHub Actions logs:
1. Go to repository → Actions
2. Click the failed "Publish to PyPI" run
3. Expand the failed job to see error logs

Common issues:
- **Wrong token**: Regenerate and update secret
- **Invalid version**: Check `pyproject.toml`
- **Already exists**: Use `skip-existing: true` (already configured)

### Manual PyPI Upload (if needed)

```bash
pip install build twine
python -m build
twine upload dist/* --repository pypi -u __token__ -p $PYPI_API_TOKEN
```

## Package Installation

After publishing, users can install with:

```bash
pip install vntts
```

With models embedded, offline usage:

```python
from vntts import TTS, STT

tts = TTS()  # Models auto-merge from .part files
stt = STT()

# Use normally - models pre-packaged
audio = tts.speak_to_bytes("Xin chào")
text = stt.recognize_from_file("audio.wav")
```

## CI/CD Features

### Automatic Testing (tests.yml)
- Runs on: push to main/develop, PRs to main
- Tests: Python 3.10, 3.11, 3.12
- Checks: linting, unit tests, package build

### Automatic Publishing (publish-pypi.yml)
- Triggers on: GitHub release creation or manual workflow dispatch
- Steps:
  1. Build distribution (.whl, .tar.gz)
  2. Check with twine
  3. Upload to PyPI
  4. Attach releases to GitHub release artifacts
