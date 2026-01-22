"""Test TTS synthesis."""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_service import ai_service
from loguru import logger

async def test_tts_synthesis():
    """Test TTS synthesis."""
    print("\n" + "="*60)
    print("🧪 Testing TTS Synthesis")
    print("="*60)
    
    try:
        test_text = "你好，这是一个测试。"
        print(f"📝 Text: {test_text}")
        
        result = await ai_service.text_to_speech(
            text=test_text,
            voice="zhitian_emo",
            format="pcm",
            sample_rate=24000
        )
        
        print(f"✅ TTS synthesis successful!")
        print(f"   - Audio data size: {len(result['audio_data'])} bytes")
        print(f"   - Duration: {result['duration_ms']} ms")
        print(f"   - Visemes count: {len(result['visemes'])}")
        
        assert "audio_data" in result, "Missing audio_data"
        assert "visemes" in result, "Missing visemes"
        assert "duration_ms" in result, "Missing duration_ms"
        assert len(result["audio_data"]) > 0, "Audio data is empty"
        assert result["duration_ms"] > 0, "Duration must be positive"
        
        print("\n✅ TTS test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Print more details about the error
        if hasattr(e, 'response'):
            print(f"\n📋 Response details:")
            print(f"   Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            try:
                print(f"   Body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
            except:
                pass
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tts_synthesis())
    sys.exit(0 if success else 1)
