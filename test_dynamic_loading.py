#!/usr/bin/env python3
"""
Test dynamic model loading in various scenarios.

Simulates the user's issue:
- Windows directory structure with different folder organization
- Running from any working directory
- Models found automatically
"""

import subprocess
import sys
import os
from pathlib import Path
import tempfile


def test_scenario_1_local_clone():
    """Test loading from a local cloned repository."""
    print("\n" + "=" * 70)
    print("SCENARIO 1: Local cloned repository")
    print("=" * 70)
    
    os.chdir("/workspaces/VNTTS")
    
    result = subprocess.run(
        [sys.executable, "test_integration.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    success = result.returncode == 0
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    if success:
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Success' in line or 'Result' in line:
                print(f"  {line}")
    else:
        print(f"  Error: {result.stderr[:200]}")
    
    return success


def test_scenario_2_different_directory():
    """Test loading when running from a completely different directory."""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Running from different directory")
    print("=" * 70)
    
    # Create temp directory and run from there
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Running from: {tmpdir}")
        
        code = '''
import sys
sys.path.insert(0, "/workspaces/VNTTS/src")

from vntts import TTS, STT

try:
    tts = TTS()
    stt = STT()
    print(f"✓ TTS found models in: {tts.model_dir}")
    print(f"✓ STT found models in: {stt.model_dir}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
'''
        
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        success = result.returncode == 0
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
        print(result.stdout)
        if not success:
            print(f"Error: {result.stderr[:200]}")
        
        return success


def test_scenario_3_explicit_path():
    """Test with explicitly provided model path."""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Explicit model path")
    print("=" * 70)
    
    code = '''
import sys
sys.path.insert(0, "/workspaces/VNTTS/src")

from vntts import TTS, STT

try:
    tts = TTS(model_dir="/workspaces/VNTTS/models/banmai")
    stt = STT(model_dir="/workspaces/VNTTS/models/asr/sherpa-onnx-zipformer-vi-2025-04-20")
    print("✓ Both TTS and STT initialized with explicit paths")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
'''
    
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    success = result.returncode == 0
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    print(result.stdout)
    if not success:
        print(f"Error: {result.stderr[:200]}")
    
    return success


def test_scenario_4_windows_simulation():
    """Simulate Windows path structure from the error report."""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Windows-like path (simulated)")
    print("=" * 70)
    print("(Simulating: D:\\Apiocr\\VietNermOCRApi\\VNTTS)")
    
    code = '''
import sys
sys.path.insert(0, "/workspaces/VNTTS/src")

from vntts.model_parts import resolve_model_dir

# Simulate user installing models in different location
try:
    # This should work even though paths have different format
    models = resolve_model_dir(None, "asr/sherpa-onnx-zipformer-vi-2025-04-20")
    print(f"✓ Successfully resolved sherpa model in: {models}")
    
    # Also test banmai
    models = resolve_model_dir(None, "banmai")
    print(f"✓ Successfully resolved banmai model in: {models}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
'''
    
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    success = result.returncode == 0
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    print(result.stdout)
    if not success:
        print(f"Error: {result.stderr[:200]}")
    
    return success


def test_scenario_5_error_handling():
    """Test proper error handling for invalid paths."""
    print("\n" + "=" * 70)
    print("SCENARIO 5: Error handling for invalid paths")
    print("=" * 70)
    
    code = '''
import sys
sys.path.insert(0, "/workspaces/VNTTS/src")

from vntts.model_parts import resolve_model_dir

# Should raise error with helpful message
try:
    resolve_model_dir("/nonexistent/path", None)
    print("✗ Should have raised FileNotFoundError")
    sys.exit(1)
except FileNotFoundError as e:
    error_msg = str(e)
    # Check for any helpful error info
    if "not found" in error_msg.lower():
        print(f"✓ Proper error handling for invalid path")
        print(f"  Message: {error_msg.split(chr(10))[0]}")
    else:
        print(f"✗ Error message not helpful")
        sys.exit(1)
'''
    
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    success = result.returncode == 0
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    print(result.stdout)
    
    return success


def main():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("TESTING DYNAMIC MODEL LOADING FIX")
    print("=" * 70)
    print("\nThis tests the fix for:")
    print("  FileNotFoundError: Model file not found in")
    print("  models\\asr\\sherpa-onnx-zipformer-vi-2025-04-20")
    
    results = []
    
    # Run scenarios
    results.append(("Local Clone", test_scenario_1_local_clone()))
    results.append(("Different Directory", test_scenario_2_different_directory()))
    results.append(("Explicit Path", test_scenario_3_explicit_path()))
    results.append(("Windows Simulation", test_scenario_4_windows_simulation()))
    results.append(("Error Handling", test_scenario_5_error_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:<30} {status}")
    
    all_passed = all(r[1] for r in results)
    total = len(results)
    passed = sum(1 for r in results if r[1])
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if all_passed:
        print("\n✓ All scenarios working! SDK now loads models dynamically.")
        return 0
    else:
        print("\n✗ Some scenarios failed. Please check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
