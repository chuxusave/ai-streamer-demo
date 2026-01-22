"""Test parsing TTS API response to understand the structure."""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
import dashscope

def test_parse_response():
    """Test parsing TTS API response."""
    print("\n" + "="*60)
    print("🧪 Testing TTS Response Parsing")
    print("="*60)
    
    api_key = settings.dashscope_api_key
    dashscope.api_key = api_key
    
    test_text = "你好，这是一个测试。"
    print(f"📝 Text: {test_text}")
    
    try:
        # Use SDK to get response
        response = dashscope.MultiModalConversation.call(
            model='qwen3-tts-flash',
            text=test_text,
            voice='Cherry',
            language_type='Chinese'
        )
        
        print(f"\n✅ API call successful!")
        print(f"   Status: {response.status_code}")
        print(f"   Response type: {type(response)}")
        
        # Inspect output structure
        if hasattr(response, 'output'):
            output = response.output
            print(f"\n📋 Output structure:")
            print(f"   Output type: {type(output)}")
            
            if hasattr(output, 'choices'):
                if output.choices is not None:
                    print(f"   Choices count: {len(output.choices)}")
                    if len(output.choices) > 0:
                        choice = output.choices[0]
                        print(f"   Choice type: {type(choice)}")
                        print(f"   Choice attributes: {dir(choice)}")
                        
                        if hasattr(choice, 'message'):
                            message = choice.message
                            print(f"   Message type: {type(message)}")
                            print(f"   Message attributes: {dir(message)}")
                            
                            if hasattr(message, 'content'):
                                content = message.content
                                print(f"   Content type: {type(content)}")
                                
                                if isinstance(content, list):
                                    print(f"   Content is a list with {len(content)} items")
                                    for i, item in enumerate(content):
                                        print(f"   Item {i}: type={type(item)}, value={str(item)[:100]}")
                                        if isinstance(item, dict):
                                            print(f"      Keys: {list(item.keys())}")
                                            if 'type' in item:
                                                print(f"      Type: {item['type']}")
                                            if 'audio' in item:
                                                audio_val = item['audio']
                                                print(f"      Audio type: {type(audio_val)}, length: {len(str(audio_val))}")
                                elif isinstance(content, str):
                                    print(f"   Content is a string, length: {len(content)}")
                                    print(f"   First 100 chars: {content[:100]}")
                else:
                    print(f"   Choices is None")
            
            # Print all output attributes
            print(f"\n📋 All output attributes:")
            for attr in dir(output):
                if not attr.startswith('_'):
                    try:
                        value = getattr(output, attr)
                        if not callable(value):
                            print(f"   {attr}: {type(value)} = {str(value)[:100]}")
                    except:
                        pass
            
            # Try to get audio using different methods
            print(f"\n🔍 Trying to extract audio:")
            
            # Method 1: Check choices
            if hasattr(output, 'choices') and output.choices is not None and len(output.choices) > 0:
                choice = output.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'audio':
                                audio_str = item.get('audio', '')
                                if isinstance(audio_str, str) and len(audio_str) > 0:
                                    print(f"   ✅ Found audio in content list!")
                                    print(f"      Audio string length: {len(audio_str)}")
                                    print(f"      First 50 chars: {audio_str[:50]}")
                                    return True
            
            print(f"   ❌ Could not extract audio")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parse_response()
    sys.exit(0 if success else 1)
