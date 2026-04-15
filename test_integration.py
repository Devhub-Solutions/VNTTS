import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

from vntts.tts import TTS
from vntts.stt import STT

def test_tts():
    print("Testing TTS with Ban Mai voice...")
    model_dir = Path("models/tts-model/vi")
    tts = TTS(lang="vi", model_dir=model_dir, model_name="banmai")
    output_path = "test_banmai.wav"
    text = "Xin chào, đây là giọng nói Ban Mai từ dự án Nghi TTS."
    tts.speak(text, output_path)
    if os.path.exists(output_path):
        print(f"TTS Success: Saved to {output_path}")
        return output_path
    else:
        print("TTS Failed: Output file not found.")
        return None

def test_stt(audio_path):
    if not audio_path:
        return
    print(f"Testing STT with {audio_path}...")
    # Use the specific directory for the new model
    model_dir = Path("models/asr/sherpa-onnx-zipformer-vi-2025-04-20")
    stt = STT(model_dir=model_dir)
    
    result = stt.recognize_from_file(audio_path)
    print(f"STT Result: {result}")
    return result

if __name__ == "__main__":
    audio = test_tts()
    if audio:
        test_stt(audio)
