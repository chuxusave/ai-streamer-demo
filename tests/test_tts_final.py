"""Final test for TTS - should work now."""
import os
import sys
import asyncio
import base64
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_service import ai_service

async def test_tts_final():
    """Final test for TTS synthesis."""
    print("\n" + "="*60)
    print("🧪 Final TTS Test")
    print("="*60)
    
    try:
        test_text = "你好，这是一个测试。"
        print(f"📝 Text: {test_text}")
        
        result = await ai_service.text_to_speech(
            text=test_text,
            voice="Cherry",
            format="pcm",
            sample_rate=24000
        )
        
        print(f"\n✅ TTS synthesis successful!")
        print(f"   Audio data size: {len(result['audio_data'])} bytes")
        print(f"   Duration: {result['duration_ms']} ms")
        print(f"   Visemes count: {len(result['visemes'])}")
        
        # Verify audio data is valid
        assert len(result['audio_data']) > 0, "Audio data is empty"
        assert result['duration_ms'] > 0, "Duration must be positive"
        
        print(f"\n✅ All checks passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tts_final())
    sys.exit(0 if success else 1)
