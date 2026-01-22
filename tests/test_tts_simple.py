"""Simple test to see actual response structure."""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load config manually
from dotenv import load_dotenv
load_dotenv()

import dashscope

def test_simple():
    """Simple test to see response structure."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set!")
        return False
    
    dashscope.api_key = api_key
    
    test_text = "你好，这是一个测试。"
    print(f"📝 Text: {test_text}")
    
    try:
        # Use SDK
        response = dashscope.MultiModalConversation.call(
            model='qwen3-tts-flash',
            text=test_text,
            voice='Cherry',
            language_type='Chinese'
        )
        
        print(f"\n✅ Status: {response.status_code}")
        
        # Convert response to dict to see structure
        if hasattr(response, 'output'):
            output = response.output
            
            # Try to convert to dict
            output_dict = {}
            for attr in dir(output):
                if not attr.startswith('_') and not callable(getattr(output, attr, None)):
                    try:
                        value = getattr(output, attr)
                        if value is not None:
                            output_dict[attr] = str(value)[:200]  # Truncate long values
                    except:
                        pass
            
            print(f"\n📋 Output attributes:")
            print(json.dumps(output_dict, indent=2, ensure_ascii=False))
            
            # Try to get audio
            if hasattr(output, 'audio_url'):
                print(f"\n🔗 Found audio_url: {output.audio_url}")
                return True
            elif hasattr(output, 'audio'):
                print(f"\n🔊 Found audio attribute")
                return True
            elif hasattr(output, 'audio_data'):
                print(f"\n📦 Found audio_data attribute")
                return True
        
        # Also check if response has methods to get audio
        if hasattr(response, 'get_audio_data'):
            try:
                audio = response.get_audio_data()
                print(f"\n✅ Got audio via get_audio_data(): {len(audio)} bytes")
                return True
            except:
                pass
        
        print(f"\n⚠️  Could not find audio in response")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple()
    sys.exit(0 if success else 1)
