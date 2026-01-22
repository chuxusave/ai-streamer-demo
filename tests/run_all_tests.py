"""Run all tests."""
import sys
import subprocess
from pathlib import Path

def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, test_file],
        cwd=Path(__file__).parent,
        capture_output=False
    )
    return result.returncode == 0

def main():
    """Run all tests."""
    test_dir = Path(__file__).parent
    test_files = [
        "test_config.py",
        "test_state.py",
        "test_llm.py",
        "test_tts_api_direct.py",  # Run this before test_tts.py to debug API
        "test_tts.py",
        "test_api.py",
    ]
    
    results = {}
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            success = run_test(str(test_path))
            results[test_file] = success
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = None
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_file, success in results.items():
        if success is True:
            print(f"✅ {test_file}")
        elif success is False:
            print(f"❌ {test_file}")
        else:
            print(f"⚠️  {test_file} (not found)")
    
    all_passed = all(s for s in results.values() if s is not None)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
