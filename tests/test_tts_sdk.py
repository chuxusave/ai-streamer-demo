"""Test TTS using dashscope SDK directly."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
import dashscope

def test_tts_with_sdk():
    """Test TTS using dashscope SDK."""
    print("\n" + "="*60)
    print("🧪 Testing TTS with DashScope SDK")
    print("="*60)
    
    api_key = settings.dashscope_api_key
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set!")
        return False
    
    dashscope.api_key = api_key
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📦 DashScope version: {getattr(dashscope, '__version__', 'unknown')}")
    
    test_text = "你好，这是一个测试。"
    print(f"📝 Text: {test_text}")
    
    # Try different SDK methods
    methods = [
        {
            "name": "dashscope.Audio.call",
            "func": lambda: dashscope.Audio.call(
                model='sambert-zhichu-v1',
                text=test_text,
                format='pcm',
                sample_rate=24000
            )
        },
        {
            "name": "dashscope.audio.tts.call",
            "func": lambda: getattr(dashscope.audio.tts, 'call', None)(
                model='sambert-zhichu-v1',
                text=test_text,
                format='pcm',
                sample_rate=24000
            ) if hasattr(dashscope, 'audio') and hasattr(dashscope.audio, 'tts') else None
        }
    ]
    
    for method in methods:
        print(f"\n🔍 Trying: {method['name']}")
        
        try:
            if method['func'] is None:
                print("   ⚠️  Method not available")
                continue
            
            response = method['func']()
            
            if response is None:
                print("   ⚠️  Method returned None")
                continue
            
            print(f"   Response type: {type(response)}")
            print(f"   Status code: {getattr(response, 'status_code', 'N/A')}")
            
            if hasattr(response, 'status_code') and response.status_code == 200:
                print("   ✅ Success!")
                
                # Try to get audio data
                if hasattr(response, 'get_audio_data'):
                    audio_data = response.get_audio_data()
                    print(f"   📦 Audio size: {len(audio_data)} bytes")
                    return True
                elif hasattr(response, 'output'):
                    output = response.output
                    print(f"   📦 Output type: {type(output)}")
                    if hasattr(output, 'keys'):
                        print(f"   📦 Output keys: {list(output.keys())}")
                    if hasattr(output, 'audio'):
                        print(f"   📦 Audio found in output")
                        return True
                elif hasattr(response, 'audio_data'):
                    print(f"   📦 Audio data size: {len(response.audio_data)} bytes")
                    return True
            else:
                error_msg = getattr(response, 'message', 'N/A')
                print(f"   ❌ Error: {error_msg}")
                
        except AttributeError as e:
            print(f"   ⚠️  Attribute not available: {e}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_tts_with_sdk()
    sys.exit(0 if success else 1)
