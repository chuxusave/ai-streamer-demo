"""AI Service for LLM script generation and TTS synthesis."""
import dashscope
from dashscope import Generation
from loguru import logger
from typing import List, Dict, Optional
import asyncio
from io import BytesIO
import json
import requests
import base64

from config import settings


# Initialize dashscope
dashscope.api_key = settings.dashscope_api_key


class AIService:
    """AI Service for generating scripts and synthesizing speech."""
    
    def __init__(self):
        self.model = "qwen-turbo"  # Use Qwen-Turbo for faster response
        self.tts_model = "sambert-zhichu-v1"  # CosyVoice model name (may vary)
    
    async def generate_scripts(self, topic: str, count: int = 5) -> List[str]:
        """Generate marketing scripts about a topic using Qwen-Turbo.
        
        Args:
            topic: The topic to generate scripts about
            count: Number of scripts to generate (default: 5)
            
        Returns:
            List of generated script strings
        """
        prompt = f"""请生成 {count} 条关于"{topic}"的简短、吸引人的营销文案。要求：
1. 每条文案不超过30个字
2. 语言生动有趣，有感染力
3. 适合直播场景播报
4. 直接输出文案，每行一条，不要编号

请开始生成："""

        try:
            logger.info(f"🤖 Generating scripts for topic: {topic}")
            
            # Call Qwen API (synchronous call, wrap in executor for async)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: Generation.call(
                    model=self.model,
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.8,
                )
            )
            
            if response.status_code == 200:
                # Extract text from response
                output_text = response.output.text.strip()
                
                # Split by lines and clean up
                scripts = [
                    line.strip() 
                    for line in output_text.split('\n') 
                    if line.strip() and not line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '*'))
                ]
                
                # If we got fewer scripts than requested, try to split by punctuation
                if len(scripts) < count:
                    # Try splitting by common sentence endings
                    import re
                    sentences = re.split(r'[。！？\n]', output_text)
                    scripts = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5][:count]
                
                # Ensure we have at least some scripts
                if not scripts:
                    scripts = [f"欢迎了解{topic}，这里有最优质的产品和服务！"]
                
                logger.info(f"✅ Generated {len(scripts)} scripts")
                return scripts[:count]
            else:
                logger.error(f"❌ Qwen API error: {response.message}")
                # Return fallback scripts
                return [f"欢迎了解{topic}，这里有最优质的产品和服务！"] * count
                
        except Exception as e:
            logger.error(f"❌ Error generating scripts: {e}")
            # Return fallback scripts on error
            return [f"欢迎了解{topic}，这里有最优质的产品和服务！"] * count
    
    async def text_to_speech(
        self, 
        text: str,
        voice: str = "zhitian_emo",
        format: str = "pcm",
        sample_rate: int = 24000
    ) -> Dict:
        """Convert text to speech using CosyVoice TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice model name (default: zhitian_emo)
            format: Audio format (pcm, wav, mp3)
            sample_rate: Sample rate in Hz (default: 24000)
            
        Returns:
            Dictionary with:
            - audio_data: bytes - Audio data
            - visemes: List[Dict] - Viseme data for lip-sync (placeholder for now)
            - duration_ms: int - Duration in milliseconds
        """
        try:
            logger.info(f"🔊 Synthesizing speech for text: {text[:50]}...")
            
            # Call CosyVoice TTS API via HTTP request
            # DashScope CosyVoice API endpoint
            loop = asyncio.get_event_loop()
            
            def call_tts():
                # Try using dashscope SDK first (MultiModalConversation)
                try:
                    response = dashscope.MultiModalConversation.call(
                        model='qwen3-tts-flash',
                        text=text,
                        voice='Cherry',
                        language_type='Chinese'
                    )
                    
                    if hasattr(response, 'status_code') and response.status_code == 200:
                        # First, try get_audio_data() method if available
                        if hasattr(response, 'get_audio_data'):
                            try:
                                audio_bytes = response.get_audio_data()
                                if audio_bytes:
                                    return {'audio_data': audio_bytes, 'format': 'direct'}
                            except Exception as e:
                                logger.debug(f"get_audio_data() failed: {e}")
                        
                        # Check response format
                        if hasattr(response, 'output'):
                            output = response.output
                            
                            # Check for audio attribute first (actual structure: output.audio.url)
                            if hasattr(output, 'audio'):
                                audio_obj = output.audio
                                # Audio is a dict/object with 'url' key (actual structure from API)
                                if hasattr(audio_obj, 'url'):
                                    audio_url = audio_obj.url
                                    if audio_url:
                                        return {'audio_url': audio_url, 'format': 'url'}
                                elif isinstance(audio_obj, dict) and 'url' in audio_obj:
                                    audio_url = audio_obj['url']
                                    if audio_url:
                                        return {'audio_url': audio_url, 'format': 'url'}
                                elif isinstance(audio_obj, str):
                                    return {'audio_data': audio_obj, 'format': 'base64'}
                            
                            # Check for audio_url (backup)
                            if hasattr(output, 'audio_url'):
                                audio_url = output.audio_url
                                if audio_url:
                                    return {'audio_url': audio_url, 'format': 'url'}
                            
                            # Check for choices structure (multimodal API format)
                            if hasattr(output, 'choices') and output.choices is not None and len(output.choices) > 0:
                                choice = output.choices[0]
                                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                    content = choice.message.content
                                    # Content might be a list of items
                                    if isinstance(content, list):
                                        for item in content:
                                            if isinstance(item, dict) and item.get('type') == 'audio':
                                                audio_str = item.get('audio', '')
                                                if isinstance(audio_str, str):
                                                    return {'audio_data': audio_str, 'format': 'base64'}
                                    elif isinstance(content, str) and len(content) > 100:
                                        # Might be base64 string directly
                                        return {'audio_data': content, 'format': 'base64'}
                            
                            # Check for audio_data attribute
                            if hasattr(output, 'audio_data'):
                                audio_data = output.audio_data
                                if isinstance(audio_data, str):
                                    return {'audio_data': audio_data, 'format': 'base64'}
                                elif isinstance(audio_data, bytes):
                                    return {'audio_data': audio_data, 'format': 'direct'}
                        
                        # If we can't extract directly, return response for later parsing
                        return {'response': response, 'format': 'sdk'}
                    else:
                        # Fall back to HTTP request
                        error_msg = getattr(response, 'message', getattr(response, 'code', 'Unknown error'))
                        raise Exception(f"SDK call failed: {error_msg}")
                except (ImportError, AttributeError) as e:
                    # SDK method not available, use HTTP
                    logger.debug(f"SDK method not available, using HTTP: {e}")
                except Exception as e:
                    # SDK call failed, fall back to HTTP
                    logger.debug(f"SDK call failed, using HTTP: {e}")
                
                # Fallback: Use HTTP request directly
                # Based on documentation, use correct endpoint and format
                headers = {
                    "Authorization": f"Bearer {settings.dashscope_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Try different endpoints and formats
                url_formats = [
                    {
                        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                        "data": {
                            "task_group": "aigc",
                            "task": "multimodal-generation",
                            "model": "qwen3-tts-flash",
                            "input": {
                                "text": text,
                                "voice": "Cherry",
                                "language_type": "Chinese"
                            }
                        }
                    },
                    {
                        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                        "data": {
                            "task_group": "aigc",
                            "task": "multimodal-generation",
                            "model": "sambert-zhichu-v1",
                            "input": {
                                "text": text
                            },
                            "parameters": {
                                "format": format,
                                "sample_rate": sample_rate
                            }
                        }
                    },
                    {
                        "url": "https://dashscope.aliyuncs.com/api/v1/services/audio/tts",
                        "data": {
                            "task_group": "aigc",
                            "task": "tts",
                            "model": "sambert-zhichu-v1",
                            "text": text,
                            "format": format,
                            "sample_rate": sample_rate
                        }
                    }
                ]
                
                last_error = None
                for url_format in url_formats:
                    try:
                        resp = requests.post(
                            url_format["url"],
                            headers=headers,
                            json=url_format["data"],
                            timeout=30
                        )
                        
                        if resp.status_code == 200:
                            return {'response': resp.json(), 'format': 'json'}
                        elif resp.status_code != 400:  # 400 means wrong format, try next
                            logger.error(f"TTS API Error {resp.status_code}: {resp.text}")
                            resp.raise_for_status()
                        else:
                            last_error = resp.text
                            continue  # Try next format
                    except Exception as e:
                        last_error = str(e)
                        continue
                
                # If all formats failed, raise error with last error message
                logger.error(f"All TTS API formats failed. Last error: {last_error}")
                raise Exception(f"TTS API call failed with all formats. Last error: {last_error}")
            
            result = await loop.run_in_executor(None, call_tts)
            
            # Parse response based on format
            audio_data = None
            
            if result.get('format') == 'direct':
                # Direct audio data from SDK
                audio_data = result['audio_data']
            elif result.get('format') == 'base64':
                # Base64 encoded audio
                audio_data = base64.b64decode(result['audio_data'])
            elif result.get('format') == 'url':
                # Audio URL, fetch it
                audio_url = result['audio_url']
                audio_resp = requests.get(audio_url, timeout=30)
                audio_resp.raise_for_status()
                audio_data = audio_resp.content
            elif result.get('format') == 'sdk':
                # SDK response (MultiModalConversation)
                response_obj = result['response']
                if hasattr(response_obj, 'output'):
                    output = response_obj.output
                    # Check for choices structure
                    if hasattr(output, 'choices') and output.choices is not None and len(output.choices) > 0:
                        choice = output.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            content = choice.message.content
                            # Content might be a list
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'audio':
                                        audio_str = item.get('audio', '')
                                        if isinstance(audio_str, str):
                                            audio_data = base64.b64decode(audio_str)
                                            break
                            elif isinstance(content, str) and len(content) > 100:
                                # Might be base64 string
                                try:
                                    audio_data = base64.b64decode(content)
                                except:
                                    pass
                    # Check for audio attribute (actual structure: output.audio.url)
                    if not audio_data and hasattr(output, 'audio'):
                        audio_obj = output.audio
                        # Audio is a dict/object with 'url' key (actual structure from API)
                        if hasattr(audio_obj, 'url'):
                            audio_url = audio_obj.url
                            if audio_url:
                                logger.info(f"📥 Fetching audio from output.audio.url: {audio_url}")
                                audio_resp = requests.get(audio_url, timeout=30)
                                audio_resp.raise_for_status()
                                audio_data = audio_resp.content
                                logger.info(f"✅ Fetched audio: {len(audio_data)} bytes")
                        elif isinstance(audio_obj, dict) and 'url' in audio_obj:
                            audio_url = audio_obj['url']
                            if audio_url:
                                logger.info(f"📥 Fetching audio from output.audio.url: {audio_url}")
                                audio_resp = requests.get(audio_url, timeout=30)
                                audio_resp.raise_for_status()
                                audio_data = audio_resp.content
                                logger.info(f"✅ Fetched audio: {len(audio_data)} bytes")
                        elif isinstance(audio_obj, str):
                            audio_data = base64.b64decode(audio_obj)
                            logger.info("✅ Extracted audio from output.audio (base64)")
                    
                    # Check for audio_url (backup)
                    if not audio_data and hasattr(output, 'audio_url'):
                        audio_url = output.audio_url
                        if audio_url:
                            logger.info(f"📥 Fetching audio from output.audio_url: {audio_url}")
                            audio_resp = requests.get(audio_url, timeout=30)
                            audio_resp.raise_for_status()
                            audio_data = audio_resp.content
                            logger.info(f"✅ Fetched audio: {len(audio_data)} bytes")
                    # Check for audio_data (direct bytes)
                    if not audio_data and hasattr(output, 'audio_data'):
                        audio_data_obj = output.audio_data
                        if isinstance(audio_data_obj, bytes):
                            audio_data = audio_data_obj
                        elif isinstance(audio_data_obj, str):
                            audio_data = base64.b64decode(audio_data_obj)
            elif result.get('format') == 'json':
                # JSON response from HTTP
                json_result = result['response']
                logger.debug(f"JSON response keys: {list(json_result.keys())}")
                
                if "output" in json_result:
                    output = json_result["output"]
                    logger.debug(f"Output type: {type(output)}, keys: {list(output.keys()) if isinstance(output, dict) else 'N/A'}")
                    
                    # Check for audio_url first (most common for TTS)
                    if isinstance(output, dict) and "audio_url" in output and output["audio_url"]:
                        audio_url = output["audio_url"]
                        logger.info(f"📥 Fetching audio from URL: {audio_url}")
                        audio_resp = requests.get(audio_url, timeout=30)
                        audio_resp.raise_for_status()
                        audio_data = audio_resp.content
                        logger.info(f"✅ Fetched audio: {len(audio_data)} bytes")
                    
                    # Check for choices structure (multimodal API format)
                    if not audio_data and isinstance(output, dict) and "choices" in output and output["choices"] is not None and len(output["choices"]) > 0:
                        choice = output["choices"][0]
                        if isinstance(choice, dict) and "message" in choice and "content" in choice["message"]:
                            content = choice["message"]["content"]
                            # Content might be a list of items
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get("type") == "audio":
                                        audio_str = item.get("audio", "")
                                        if isinstance(audio_str, str):
                                            audio_data = base64.b64decode(audio_str)
                                            logger.info("✅ Extracted audio from choices.content list")
                                            break
                            elif isinstance(content, str) and len(content) > 100:
                                # Might be base64 string directly
                                try:
                                    audio_data = base64.b64decode(content)
                                    logger.info("✅ Extracted audio from choices.content string")
                                except Exception as e:
                                    logger.debug(f"Failed to decode content as base64: {e}")
                    
                    # Check for audio field FIRST (actual structure: output.audio.url)
                    # This is the most common structure based on test results
                    if not audio_data and isinstance(output, dict) and "audio" in output:
                        audio_obj = output["audio"]
                        if isinstance(audio_obj, dict):
                            # Audio is a dict with 'url' key (actual structure from API)
                            if "url" in audio_obj and audio_obj["url"]:
                                audio_url = audio_obj["url"]
                                logger.info(f"📥 Fetching audio from output.audio.url: {audio_url}")
                                try:
                                    audio_resp = requests.get(audio_url, timeout=30)
                                    audio_resp.raise_for_status()
                                    audio_data = audio_resp.content
                                    logger.info(f"✅ Fetched audio: {len(audio_data)} bytes")
                                except Exception as e:
                                    logger.error(f"❌ Failed to fetch audio from URL: {e}")
                            elif "data" in audio_obj and audio_obj["data"]:
                                # Audio data might be in data field (usually empty, but check)
                                audio_data_str = audio_obj["data"]
                                if isinstance(audio_data_str, str) and len(audio_data_str) > 0:
                                    audio_data = base64.b64decode(audio_data_str)
                                    logger.info("✅ Extracted audio from output.audio.data")
                        elif isinstance(audio_obj, str):
                            # Audio is a base64 string directly
                            audio_data = base64.b64decode(audio_obj)
                            logger.info("✅ Extracted audio from output.audio (base64)")
                    
                    # Check for audio_data field
                    if not audio_data and isinstance(output, dict) and "audio_data" in output:
                        audio_data_obj = output["audio_data"]
                        if isinstance(audio_data_obj, str):
                            audio_data = base64.b64decode(audio_data_obj)
                            logger.info("✅ Extracted audio from output.audio_data (base64)")
                        elif isinstance(audio_data_obj, bytes):
                            audio_data = audio_data_obj
                            logger.info("✅ Extracted audio from output.audio_data (bytes)")
                
                elif "data" in json_result:
                    # Alternative response format
                    if isinstance(json_result["data"], str):
                        audio_data = base64.b64decode(json_result["data"])
                        logger.info("✅ Extracted audio from data field (base64)")
                    else:
                        audio_data = json_result["data"]
                        logger.info("✅ Extracted audio from data field (direct)")
            
            if not audio_data:
                raise Exception(f"Could not extract audio data from API response. Result format: {result.get('format')}, Keys: {list(result.keys())}")
            
            # Calculate duration (approximate)
            # For PCM: duration = len(audio_data) / (sample_rate * channels * bytes_per_sample)
            # Assuming mono, 16-bit (2 bytes per sample)
            channels = 1
            bytes_per_sample = 2
            duration_seconds = len(audio_data) / (sample_rate * channels * bytes_per_sample)
            duration_ms = int(duration_seconds * 1000)
            
            # Generate placeholder visemes (will be enhanced in Phase 3)
            # For now, create simple viseme data based on text length
            visemes = self._generate_visemes_placeholder(text, duration_ms)
            
            logger.info(f"✅ Synthesized audio: {duration_ms}ms, {len(audio_data)} bytes")
            
            return {
                "audio_data": audio_data,
                "visemes": visemes,
                "duration_ms": duration_ms,
            }
                
        except Exception as e:
            logger.error(f"❌ Error in TTS synthesis: {e}")
            raise
    
    def _generate_visemes_placeholder(self, text: str, duration_ms: int) -> List[Dict]:
        """Generate placeholder viseme data for lip-sync.
        
        This is a placeholder implementation. In Phase 3, we'll extract
        actual visemes from TTS phoneme timestamps.
        
        Args:
            text: Input text
            duration_ms: Audio duration in milliseconds
            
        Returns:
            List of viseme dictionaries with offset and coefficients
        """
        # Simple placeholder: create visemes at regular intervals
        num_visemes = max(10, len(text) // 3)  # At least 10 visemes
        interval_ms = duration_ms / num_visemes
        
        visemes = []
        for i in range(num_visemes):
            # Placeholder: simple blend shape coefficients (52 values)
            # In real implementation, these would be extracted from TTS phoneme data
            coefficients = [0.0] * 52
            # Simple animation: open/close mouth based on position
            mouth_open = 0.3 + 0.3 * (i % 2)  # Alternate between 0.3 and 0.6
            coefficients[0] = mouth_open  # First coefficient for mouth opening
            
            visemes.append({
                "offset": i * interval_ms / 1000.0,  # Offset in seconds
                "coefficients": coefficients,
            })
        
        return visemes


# Global AI service instance
ai_service = AIService()
