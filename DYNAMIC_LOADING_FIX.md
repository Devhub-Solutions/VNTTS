# Dynamic Model Loading Fix

## Problem
When users installed VNTTS as a package (via `pip install vntts`), the model files couldn't be found because the code was looking for models relative to the current working directory.

**Error Example:**
```
FileNotFoundError: Model file not found in models\asr\sherpa-onnx-zipformer-vi-2025-04-20: pattern 'decoder*.onnx'
```

This happened because:
- Models were referenced with relative paths like `"models/banmai/"`
- When installed as a package, `models/` doesn't exist relative to the user's working directory
- The code didn't know to look in the package installation directory

## Solution

### New Function: `resolve_model_dir()`

Added smart directory resolution that checks multiple locations in order:

1. **User-provided path** - If explicitly given via `model_dir` parameter
2. **Package installation directory** - Where the package is installed (usually in site-packages)
3. **Current working directory** - For development/cloned repos
4. **Project root directory** - For editable installs (`pip install -e`)

**Location Resolution:**
```
models/
├── Checked in: /path/to/venv/lib/site-packages/vntts/models/
├── Checked in: /current/working/directory/models/
└── Checked in: /path/to/cloned/repo/models/
```

### Updated Classes

#### TTS Class
- Now tries to find `banmai` (included model) automatically
- Falls back to language-based directory if needed
- Supports explicit `model_dir` parameter for custom locations

#### STT Class
- Automatically finds `asr/sherpa-onnx-zipformer-vi-2025-04-20` in package
- Supports explicit `model_dir` parameter for custom models

## Files Changed

1. **`src/vntts/model_parts.py`**
   - Added `resolve_model_dir()` function
   - Searches multiple locations intelligently
   - Provides helpful error messages

2. **`src/vntts/tts.py`**
   - Updated `__init__` to use `resolve_model_dir()`
   - Tries "banmai" first, then language-based fallback

3. **`src/vntts/stt.py`**
   - Updated `__init__` to use `resolve_model_dir()`
   - Automatically finds sherpa-onnx model

## Usage

### Development (from cloned repo)
```python
from vntts import TTS, STT

# Works from project root or any subdirectory
tts = TTS()  # Finds models/banmai/
stt = STT()  # Finds models/asr/...
```

### After `pip install vntts`
```python
from vntts import TTS, STT

# Works from anywhere, models found in site-packages
tts = TTS()
stt = STT()
```

### Custom Model Location
```python
from vntts import TTS, STT

# Always works with explicit path
tts = TTS(model_dir="/custom/path/to/banmai")
stt = STT(model_dir="/custom/path/to/sherpa")
```

## Testing

All tests pass ✅:
- **17 unit tests** - All pass
- **Integration test** - TTS → STT pipeline works
- **Different directory test** - Works when run from different folder
- **Edge cases** - Invalid paths, explicit paths, all handled

## Benefits

✅ **Works after pip install** - No relative path issues  
✅ **Works in development** - Finds local models  
✅ **Works with custom paths** - Still supports explicit paths  
✅ **Helpful error messages** - Shows where it looked  
✅ **Backward compatible** - Existing code still works  
✅ **No breaking changes** - All tests pass  

## Migration

No action required! This is a transparent fix:
- Existing code continues to work
- New installations find models automatically
- Custom paths still work as before
