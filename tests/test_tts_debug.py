"""Debug TTS response to see actual structure."""
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
import requests

def test_debug():
    """Debug TTS response structure."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set!")
        return False
    
    dashscope.api_key = api_key
    test_text = "你好，这是一个测试。"
    
    print("\n" + "="*60)
    print("🔍 Method 1: Using SDK")
    print("="*60)
    
    try:
        response = dashscope.MultiModalConversation.call(
            model='qwen3-tts-flash',
            text=test_text,
            voice='Cherry',
            language_type='Chinese'
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response type: {type(response)}")
        
        # Check for get_audio_data method
        if hasattr(response, 'get_audio_data'):
            try:
                audio = response.get_audio_data()
                print(f"✅ get_audio_data() works! Size: {len(audio)} bytes")
                return True
            except Exception as e:
                print(f"❌ get_audio_data() failed: {e}")
        
        # Check output
        if hasattr(response, 'output'):
            output = response.output
            print(f"Output type: {type(output)}")
            
            # List all attributes
            attrs = [attr for attr in dir(output) if not attr.startswith('_')]
            print(f"Output attributes: {attrs}")
            
            # Check specific attributes
            for attr in ['audio_url', 'audio', 'audio_data', 'choices']:
                if hasattr(output, attr):
                    value = getattr(output, attr)
                    print(f"  {attr}: {type(value)} = {str(value)[:200]}")
                    if attr == 'audio_url' and value:
                        print(f"  ✅ Found audio_url!")
                        return True
        
    except Exception as e:
        print(f"❌ SDK Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("🔍 Method 2: Using HTTP API")
    print("="*60)
    
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "task_group": "aigc",
            "task": "multimodal-generation",
            "model": "qwen3-tts-flash",
            "input": {
                "text": test_text,
                "voice": "Cherry",
                "language_type": "Chinese"
            }
        }
        
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"Response keys: {list(result.keys())}")
            
            if "output" in result:
                output = result["output"]
                print(f"Output type: {type(output)}")
                print(f"Output keys: {list(output.keys()) if isinstance(output, dict) else 'N/A'}")
                
                # Print full output structure
                print(f"\nFull output structure:")
                print(json.dumps(output, indent=2, ensure_ascii=False)[:1000])
                
                # Check for audio_url
                if isinstance(output, dict) and "audio_url" in output:
                    print(f"\n✅ Found audio_url: {output['audio_url']}")
                    return True
                
                # Check for audio
                if isinstance(output, dict) and "audio" in output:
                    audio_val = output["audio"]
                    print(f"\nFound audio: type={type(audio_val)}")
                    if isinstance(audio_val, str):
                        print(f"  Audio is string, length: {len(audio_val)}")
                        return True
                    elif isinstance(audio_val, dict):
                        print(f"  Audio is dict, keys: {list(audio_val.keys())}")
        
    except Exception as e:
        print(f"❌ HTTP Error: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_debug()
    sys.exit(0 if success else 1)
