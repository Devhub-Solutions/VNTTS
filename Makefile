.PHONY: help install test lint format clean build publish

help:
	@echo "VNTTS Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test             Run tests"
	@echo "  make lint             Check code quality"
	@echo "  make format           Auto-format code"
	@echo "  make type-check       Run type checking"
	@echo ""
	@echo "Building:"
	@echo "  make build            Build distribution"
	@echo "  make build-clean      Clean and rebuild"
	@echo ""
	@echo "Release:"
	@echo "  make publish          Publish to PyPI (local, use 'gh release' for CI)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove build artifacts"
	@echo "  make clean-all        Remove all generated files"

install:
	pip install -e ".[dev]"
	pip install build twine black isort pyright

test:
	pytest tests/ -v --cov=src/vntts --cov-report=term-only

test-fast:
	pytest tests/ -v --no-cov

test-specific:
	@read -p "Enter test path (e.g. tests/test_tts.py::TestTTSInit): " test_path; \
	pytest $$test_path -v

lint:
	@echo "Checking code quality..."
	pyright src/ || true
	pylint src/vntts --disable=all --enable=E,F,W || true
	@echo "✓ Lint check complete"

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "✓ Formatting complete"

type-check:
	pyright src/ --outputjson | python -m json.tool || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/
	@echo "✓ Cleaned build artifacts"

clean-all: clean
	rm -rf .venv/ .pytest_cache/
	@echo "✓ Cleaned all generated files"

build:
	python -m build
	@echo "✓ Built distribution"
	@ls -lh dist/

build-clean: clean build
	@echo "✓ Clean build complete"
	twine check dist/*
	@echo "✓ Distribution validated"

publish:
	@echo "Warning: Use 'gh release create' for GitHub Actions auto-publish"
	@echo "Local publish (manual):"
	pip install twine
	twine upload dist/* -u __token__ -p $$PYPI_API_TOKEN

git-push:
	git add .
	git commit -m "$(MSG)"
	git push origin main

release-patch:
	@echo "Patch release (0.1.0 → 0.1.1)"
	@read -p "Enter new version (e.g. 0.1.1): " version; \
	sed -i.bak "s/version = .*/version = \"$$version\"/" pyproject.toml; \
	rm pyproject.toml.bak; \
	git add pyproject.toml; \
	git commit -m "Bump version to $$version"; \
	git push origin main; \
	gh release create v$$version --generate-notes

dev-setup:
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && make install
	@echo "✓ Development environment ready"
	@echo "Activate with: source .venv/bin/activate"

run-example:
	python examples.py

.DEFAULT_GOAL := help
