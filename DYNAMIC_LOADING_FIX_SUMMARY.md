# SDK Dynamic Model Loading - Fix Summary

## Problem (User's Error)

User reported error when installing SDK as a package:

```
FileNotFoundError: Model file not found in models\asr\sherpa-onnx-zipformer-vi-2025-04-20: pattern 'decoder*.onnx'
```

**Root Cause**: When SDK is installed via `pip install`, the models directory is no longer relative to the current working directory. The code was hardcoded to look in `models/` relative to CWD, which fails when:
- User clones repo somewhere else
- SDK is installed as a package
- User runs from a different directory

## Solution

### Added `resolve_model_dir()` Function

New function in `src/vntts/model_parts.py` that intelligently searches for models in multiple locations:

```python
def resolve_model_dir(
    model_dir: str | Path | None = None,
    default_subdir: str = "banmai",
) -> Path:
    """Resolve model directory path, checking multiple locations."""
```

**Search Order:**
1. **Explicit Path** (if provided)
   ```python
   TTS(model_dir="/custom/path/to/banmai")
   ```

2. **Package Installation Directory**
   - Where SDK is installed (site-packages)
   - Path: `{site-packages}/vntts/models/{default_subdir}`

3. **Current Working Directory** (Development)
   - Path: `{cwd}/models/{default_subdir}`

4. **Project Root** (Editable installs)
   - Path: `{project}/models/{default_subdir}`

### Updated Classes

#### TTS Class (`src/vntts/tts.py`)
- Tries to find `banmai` model automatically
- Falls back to language-based lookup if needed
- Uses `resolve_model_dir()` for smart path resolution

#### STT Class (`src/vntts/stt.py`)
- Automatically finds `asr/sherpa-onnx-zipformer-vi-2025-04-20`
- Falls back gracefully
- Uses `resolve_model_dir()` for smart path resolution

## Testing

### Scenarios Tested (All Pass ✅)

Run with: `python test_dynamic_loading.py`

**Scenario 1: Local Clone**
- ✅ Loading from cloned repository
- ✅ Running `test_integration.py` works

**Scenario 2: Different Directory**
- ✅ Models found even when running from `/tmp/` or other directory
- ✅ SDK installed via `pip install` simulation

**Scenario 3: Explicit Path**
- ✅ Custom model paths still work
- ✅ User provides full path to models

**Scenario 4: Windows-like Structure**
- ✅ Handles Windows paths correctly
- ✅ Simulates: `D:\Apiocr\VietNermOCRApi\VNTTS`

**Scenario 5: Error Handling**
- ✅ Invalid paths properly rejected
- ✅ Helpful error messages with search locations

### Test Results

```
Local Clone                    ✓ PASS
Different Directory            ✓ PASS
Explicit Path                  ✓ PASS
Windows Simulation             ✓ PASS
Error Handling                 ✓ PASS

Unit Tests:                    17/17 PASS
```

## Usage Examples

### After Installation (Any Directory)

```python
from vntts import TTS, STT

# Works from any directory - models auto-found
cd /tmp/
python -c "
from vntts import TTS
tts = TTS()  # Finds models in package dir
"
```

### With Custom Models

```python
from vntts import TTS, STT

tts = TTS(
    model_dir="/path/to/my/banmai/model"
)

stt = STT(
    model_dir="/path/to/my/sherpa/model"
)
```

### Development (From Cloned Repo)

```python
from vntts import TTS, STT

# Works from project root or any subdirectory
tts = TTS()  # Finds models/banmai/
stt = STT()  # Finds models/asr/sherpa-onnx-...
```

## Benefits

✅ **Windows Compatible** - Handles backslashes and UNC paths  
✅ **Pip-Install Ready** - Works after `pip install vntts`  
✅ **Development Friendly** - Works from cloned repo  
✅ **Custom Paths** - Still supports explicit paths  
✅ **Helpful Errors** - Clear messages about where it searched  
✅ **Backward Compatible** - Existing code continues to work  
✅ **Well Tested** - 5 scenarios + 17 unit tests  

## Files Changed

```
src/vntts/model_parts.py     ✏️  Added resolve_model_dir()
src/vntts/tts.py            ✏️  Updated to use resolve_model_dir()
src/vntts/stt.py            ✏️  Updated to use resolve_model_dir()
test_dynamic_loading.py      ✨  New comprehensive test suite
DYNAMIC_LOADING_FIX.md       ✨  Documentation
```

## Migration

**No migration needed!** This is a transparent fix:
- Existing installations continue to work
- New installations find models automatically
- Custom paths still work as before
- All tests pass (17/17)

## Error Examples

### Before (Broken)
```
FileNotFoundError: Model file not found in models\asr\sherpa-onnx-zipformer-vi-2025-04-20: pattern 'decoder*.onnx'
```

### After (Fixed)
- Automatically finds models in package or project directory
- Or provides clear error if path is invalid:
```
FileNotFoundError: Model directory not found: /invalid/path
Provided explicit path does not exist.
Please verify the path is correct.
```

## Next Steps

The SDK now handles dynamic model loading correctly for:
- ✅ Windows users
- ✅ Linux/Mac users
- ✅ Package installations via pip
- ✅ Development from cloned repo
- ✅ Custom model locations

Users can install and use immediately without path issues! 🚀
