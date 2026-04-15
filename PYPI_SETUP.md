# PyPI Setup Checklist

## ✅ Completed Setup

Your VNTTS project is now ready for PyPI publishing!

### Files Created:
- ✅ `.github/workflows/publish-pypi.yml` - Auto-publish to PyPI on release
- ✅ `.github/workflows/tests.yml` - CI/CD for Python 3.10-3.12
- ✅ `RELEASE.md` - Complete release guide
- ✅ `CONTRIBUTING.md` - Developer guidelines

## 📋 Next Steps to Enable Publishing

### Step 1: Create PyPI API Token

```bash
# Go to https://pypi.org/account/
# Login → API tokens → Create token
# Scope: "Entire Account"
# Copy the token (format: pypi-...)
```

### Step 2: Add Secret to GitHub

```bash
# Go to your GitHub repo
# Settings → Secrets and variables → Actions
# New repository secret:
#   Name: PYPI_API_TOKEN
#   Value: [paste token from PyPI]
```

Or use GitHub CLI:
```bash
gh secret set PYPI_API_TOKEN --body "pypi-..."
```

### Step 3: Create a Release

```bash
# Update version in pyproject.toml
# version = "0.1.0" → version = "0.1.1"

git add pyproject.toml
git commit -m "Bump version to 0.1.1"
git push origin main

# Create GitHub release (auto-triggers publish)
gh release create v0.1.1 --generate-notes
```

Or via GitHub Web:
1. Go to Releases → "Create a new release"
2. Tag: v0.1.1
3. Generate release notes
4. Publish

## 🔄 Workflow Details

### Publish Workflow (`publish-pypi.yml`)
**Triggers on:**
- Creating a GitHub release
- Manual workflow dispatch

**Process:**
1. Checkout code
2. Set up Python 3.11
3. Install build tools
4. Build distribution (.whl + .tar.gz)
5. Check with twine
6. Upload to PyPI
7. Attach artifacts to release

### Tests Workflow (`tests.yml`)
**Triggers on:**
- Push to main/develop
- Pull requests to main

**Tests:**
- Python 3.10, 3.11, 3.12
- Unit tests
- Type checking
- Package build verification

## 📦 Installation (after publishing)

Users can then install with:
```bash
pip install vntts
```

With embedded models - completely offline!

## 🧪 Test Before Release

```bash
# Run locally
pytest tests/ -v

# Build package
pip install build
python -m build

# Check package
pip install twine
twine check dist/*
```

## 📝 Version Numbering

Use semantic versioning in `pyproject.toml`:
- `0.1.0` → First major version
- `0.2.0` → New features
- `0.2.1` → Bug fixes

Release tag should match: `v0.2.1`

## 🐛 Troubleshooting

### Publish failed?
- Check GitHub Actions logs
- Verify PYPI_API_TOKEN secret is set correctly
- Verify version in pyproject.toml

### Token issues?
```bash
# Regenerate on PyPI
# Settings → API tokens → Regenerate
# Update GitHub secret with new token
```

### Already published?
- Increment version number
- Create new release with new version

## 📚 More Info

See `RELEASE.md` for:
- Detailed release process
- Manual PyPI upload
- Version management
- Release checklist

See `CONTRIBUTING.md` for:
- Development setup
- Coding standards
- Testing guidelines

## 🚀 Quick Start Summary

```bash
# 1. Add PYPI_API_TOKEN to GitHub secrets

# 2. Update version
vim pyproject.toml  # 0.1.0 → 0.1.1

# 3. Commit
git add pyproject.toml
git commit -m "Bump version to 0.1.1"
git push

# 4. Create release (auto-publishes)
gh release create v0.1.1 --generate-notes

# 5. Verify on PyPI
# https://pypi.org/project/vntts/
```

That's it! 🎉
