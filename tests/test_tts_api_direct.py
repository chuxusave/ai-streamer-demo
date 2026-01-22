"""Test TTS API directly to debug the issue."""
import os
import sys
import requests
import base64
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

def test_tts_api_direct():
    """Test TTS API directly with different formats."""
    print("\n" + "="*60)
    print("🧪 Testing TTS API Directly")
    print("="*60)
    
    api_key = settings.dashscope_api_key
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set!")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    test_text = "你好，这是一个测试。"
    print(f"📝 Text: {test_text}")
    
    # Try different API endpoints and formats
    # Based on documentation, correct format should use:
    # - task_group: "aigc"
    # - task: "multimodal-generation"
    # - endpoint: /api/v1/services/aigc/multimodal-generation/generation
    endpoints = [
        {
            "name": "Qwen TTS with correct task_group and task",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            "data": {
                "task_group": "aigc",
                "task": "multimodal-generation",
                "model": "qwen3-tts-flash",
                "input": {
                    "text": test_text,
                    "voice": "Cherry",
                    "language_type": "Chinese"
                }
            }
        },
        {
            "name": "Qwen TTS with sambert model",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            "data": {
                "task_group": "aigc",
                "task": "multimodal-generation",
                "model": "sambert-zhichu-v1",
                "input": {
                    "text": test_text
                },
                "parameters": {
                    "format": "pcm",
                    "sample_rate": 24000
                }
            }
        },
        {
            "name": "DashScope MultiModalConversation SDK",
            "use_sdk": True,
            "model": "qwen3-tts-flash",
            "text": test_text,
            "voice": "Cherry",
            "language_type": "Chinese"
        },
        {
            "name": "Old endpoint with task_group (backup)",
            "url": "https://dashscope.aliyuncs.com/api/v1/services/audio/tts",
            "data": {
                "task_group": "aigc",
                "task": "tts",
                "model": "sambert-zhichu-v1",
                "text": test_text,
                "format": "pcm",
                "sample_rate": 24000
            }
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        print(f"\n🔍 Trying: {endpoint['name']}")
        
        try:
            if endpoint.get('use_sdk'):
                # Try using dashscope SDK
                print(f"   Using dashscope SDK...")
                import dashscope
                dashscope.api_key = api_key
                
                try:
                    # Try MultiModalConversation.call for TTS
                    response = dashscope.MultiModalConversation.call(
                        model=endpoint['model'],
                        text=endpoint['text'],
                        voice=endpoint.get('voice', 'Cherry'),
                        language_type=endpoint.get('language_type', 'Chinese')
                    )
                    
                    print(f"   Status: {getattr(response, 'status_code', 'N/A')}")
                    
                    if hasattr(response, 'status_code') and response.status_code == 200:
                        print(f"   ✅ Success! Response type: {type(response)}")
                        if hasattr(response, 'output'):
                            output = response.output
                            print(f"   📦 Output type: {type(output)}")
                            if hasattr(output, 'audio'):
                                print(f"   📦 Audio found in output")
                                return True
                            elif hasattr(output, 'choices') and len(output.choices) > 0:
                                choice = output.choices[0]
                                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                    print(f"   📦 Content found in message")
                                    return True
                        return True
                    else:
                        error_msg = getattr(response, 'message', getattr(response, 'code', 'N/A'))
                        print(f"   ❌ Error: {error_msg}")
                except ImportError as e:
                    print(f"   ⚠️  SDK not available: {e}")
                except Exception as e:
                    print(f"   ❌ SDK Exception: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # Use HTTP request
                print(f"   URL: {endpoint['url']}")
                print(f"   Data: {json.dumps(endpoint['data'], ensure_ascii=False, indent=2)}")
                
                resp = requests.post(
                    endpoint['url'],
                    headers=headers,
                    json=endpoint['data'],
                    timeout=30
                )
                
                print(f"   Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    result = resp.json()
                    print(f"   ✅ Success! Response keys: {list(result.keys())}")
                    
                    # Debug: print output structure
                    if "output" in result:
                        output = result["output"]
                        print(f"   📋 Output type: {type(output)}")
                        if isinstance(output, dict):
                            print(f"   📋 Output keys: {list(output.keys())}")
                        
                        # Try to extract audio - check different possible structures
                        if isinstance(output, dict):
                            # Check for choices structure (common in multimodal APIs)
                            if "choices" in output and len(output["choices"]) > 0:
                                choice = output["choices"][0]
                                print(f"   📋 Choice keys: {list(choice.keys()) if isinstance(choice, dict) else 'N/A'}")
                                
                                if isinstance(choice, dict) and "message" in choice:
                                    message = choice["message"]
                                    if isinstance(message, dict) and "content" in message:
                                        content = message["content"]
                                        print(f"   📋 Content type: {type(content)}")
                                        
                                        # Content might be a list of items
                                        if isinstance(content, list) and len(content) > 0:
                                            for item in content:
                                                if isinstance(item, dict) and item.get("type") == "audio":
                                                    audio_data = item.get("audio", "")
                                                    if isinstance(audio_data, str):
                                                        audio_bytes = base64.b64decode(audio_data)
                                                        print(f"   📦 Audio size: {len(audio_bytes)} bytes")
                                                        return True
                                        elif isinstance(content, str) and len(content) > 100:
                                            # Might be base64 string directly
                                            try:
                                                audio_bytes = base64.b64decode(content)
                                                print(f"   📦 Audio size: {len(audio_bytes)} bytes")
                                                return True
                                            except:
                                                pass
                            
                            # Check for direct audio field
                            if "audio" in output:
                                audio_data = output["audio"]
                                if isinstance(audio_data, str):
                                    audio_bytes = base64.b64decode(audio_data)
                                    print(f"   📦 Audio size: {len(audio_bytes)} bytes")
                                    return True
                            elif "audio_url" in output:
                                print(f"   🔗 Audio URL: {output['audio_url']}")
                                return True
                    elif "data" in result:
                        print(f"   📦 Data type: {type(result['data'])}")
                        return True
                    
                    # If we got here, print full structure for debugging
                    print(f"   ⚠️  Could not extract audio. Full output: {json.dumps(result.get('output', {}), indent=2)[:500]}")
                else:
                    print(f"   ❌ Error: {resp.status_code}")
                    print(f"   Response: {resp.text[:500]}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_tts_api_direct()
    sys.exit(0 if success else 1)
