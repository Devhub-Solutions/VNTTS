"""
VNTTS - Vietnamese Text-to-Speech & Speech-to-Text Library

Simple usage examples
"""

from pathlib import Path
from vntts import TTS, STT

# ============================================================================
# TEXT-TO-SPEECH (TTS) EXAMPLE
# ============================================================================

def example_tts():
    """Convert Vietnamese text to speech using Ban Mai voice."""
    
    # Initialize TTS with Ban Mai model
    tts = TTS(lang="vi", model_dir="models/banmai", model_name="banmai")
    
    # Text to synthesize
    text = "Xin chào, đây là giọng nói Ban Mai"
    
    # Method 1: Save to WAV file
    output_file = Path("output_audio.wav")
    tts.speak(text, str(output_file))
    print(f"✓ Audio saved to {output_file}")
    
    # Method 2: Get audio as bytes (for streaming, API, etc.)
    audio_bytes = tts.speak_to_bytes(text)
    print(f"✓ Audio as bytes: {len(audio_bytes)} bytes")
    
    return output_file


# ============================================================================
# SPEECH-TO-TEXT (STT) EXAMPLE
# ============================================================================

def example_stt(audio_path: str | Path):
    """Recognize Vietnamese speech from audio file."""
    
    # Initialize STT
    stt = STT(
        lang="vi-VN",
        model_dir="models/asr/sherpa-onnx-zipformer-vi-2025-04-20",
        provider="cpu",
        num_threads=1
    )
    
    # Recognize from audio file
    result = stt.recognize_from_file(audio_path)
    print(f"✓ Recognized text: {result}")
    
    return result


# ============================================================================
# TTS + STT PIPELINE (ROUND-TRIP)
# ============================================================================

def example_pipeline():
    """Complete TTS→STT round-trip example."""
    
    print("=" * 60)
    print("VNTTS Pipeline Example: TTS → STT Round-trip")
    print("=" * 60)
    
    # Step 1: Generate speech from text
    print("\n[1] Generating speech from text...")
    tts = TTS(lang="vi", model_dir="models/banmai", model_name="banmai")
    input_text = "Tôi yêu lập trình Python"
    
    audio_file = Path("pipeline_demo.wav")
    tts.speak(input_text, str(audio_file))
    print(f"    Text: '{input_text}'")
    print(f"    Audio: {audio_file} ({audio_file.stat().st_size} bytes)")
    
    # Step 2: Recognize speech to text
    print("\n[2] Recognizing speech from audio...")
    stt = STT(model_dir="models/asr/sherpa-onnx-zipformer-vi-2025-04-20")
    recognized_text = stt.recognize_from_file(audio_file)
    print(f"    Recognized: '{recognized_text}'")
    
    # Step 3: Compare
    print("\n[3] Result:")
    print(f"    Original:   '{input_text}'")
    print(f"    Recognized: '{recognized_text}'")
    
    # Cleanup
    audio_file.unlink()
    print(f"\n✓ Pipeline completed (demo file cleaned up)")


# ============================================================================
# DEPLOYMENT NOTES
# ============================================================================

"""
## Using VNTTS in your project:

### Installation
pip install vntts

### Offline Usage
The library includes split model files that are:
- Automatically merged on first load
- No Git LFS required
- Works completely offline (no internet needed after installation)

### Customization

#### Use different TTS voice
```python
tts = TTS(lang="vi", model_dir="path/to/models", model_name="your_voice")
```

#### Use different STT model
```python
stt = STT(model_dir="path/to/sherpa-model")
```

#### Docker deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

ENTRYPOINT ["python", "-c", "from vntts import TTS; tts = TTS(); tts.speak('Hello', 'output.wav')"]
```

### Performance Notes
- TTS: ~2-5 seconds per sentence on CPU
- STT: ~2-10x real-time on CPU
- GPU support available (set `use_cuda=True` for TTS)

### Troubleshooting
- Model files are auto-merged from `.part*` files on first load
- If merge fails, run: `python scripts/merge_model.py models/`
- Check checksums: `python scripts/merge_model.py <file> --verify-checksum`
"""


if __name__ == "__main__":
    # Run examples
    print("\n" + "=" * 60)
    print("VNTTS Examples")
    print("=" * 60 + "\n")
    
    # Example 1: TTS
    print("[Example 1] Text-to-Speech")
    audio_path = example_tts()
    
    # Example 2: STT (requires audio from Example 1)
    print("\n[Example 2] Speech-to-Text")
    example_stt(audio_path)
    
    # Example 3: Full pipeline
    print("\n[Example 3] Full Pipeline")
    example_pipeline()
    
    print("\n✓ All examples completed!")
