"""Test LLM script generation."""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_service import ai_service
from loguru import logger

async def test_llm_generate_scripts():
    """Test LLM script generation."""
    print("\n" + "="*60)
    print("🧪 Testing LLM Script Generation")
    print("="*60)
    
    try:
        topic = "咖啡机"
        print(f"📝 Topic: {topic}")
        
        scripts = await ai_service.generate_scripts(topic, count=3)
        
        print(f"✅ Generated {len(scripts)} scripts:")
        for i, script in enumerate(scripts, 1):
            print(f"   {i}. {script}")
        
        assert len(scripts) > 0, "No scripts generated"
        assert all(isinstance(s, str) for s in scripts), "Scripts must be strings"
        assert all(len(s) > 0 for s in scripts), "Scripts must not be empty"
        
        print("\n✅ LLM test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_generate_scripts())
    sys.exit(0 if success else 1)
