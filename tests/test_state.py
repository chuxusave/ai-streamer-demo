"""Test state management."""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state import GlobalState, AudioItem

async def test_state_management():
    """Test state management."""
    print("\n" + "="*60)
    print("🧪 Testing State Management")
    print("="*60)
    
    try:
        state = GlobalState()
        
        # Test topic management
        print("📝 Testing topic management...")
        await state.set_topic("测试主题")
        topic = await state.get_topic()
        assert topic == "测试主题", f"Expected '测试主题', got '{topic}'"
        print("   ✅ Topic management works")
        
        # Test streaming state
        print("📡 Testing streaming state...")
        await state.set_streaming(True)
        assert await state.is_currently_streaming() == True
        await state.set_streaming(False)
        assert await state.is_currently_streaming() == False
        print("   ✅ Streaming state works")
        
        # Test playlist management
        print("🎵 Testing playlist management...")
        test_item = AudioItem(
            text="测试文本",
            audio_data=b"test audio data",
            visemes=[],
            duration_ms=1000,
            created_at=datetime.now()
        )
        
        await state.add_to_playlist(test_item)
        size = await state.get_playlist_size()
        assert size == 1, f"Expected size 1, got {size}"
        print(f"   ✅ Added item, playlist size: {size}")
        
        item = await state.pop_from_playlist()
        assert item is not None, "Failed to pop item"
        assert item.text == "测试文本", "Item text mismatch"
        print("   ✅ Popped item successfully")
        
        size = await state.get_playlist_size()
        assert size == 0, f"Expected size 0, got {size}"
        print("   ✅ Playlist is empty after pop")
        
        # Test batch add
        items = [
            AudioItem(
                text=f"文本{i}",
                audio_data=b"data",
                visemes=[],
                duration_ms=1000,
                created_at=datetime.now()
            )
            for i in range(5)
        ]
        await state.add_batch_to_playlist(items)
        size = await state.get_playlist_size()
        assert size == 5, f"Expected size 5, got {size}"
        print(f"   ✅ Batch added {len(items)} items")
        
        await state.clear_playlist()
        size = await state.get_playlist_size()
        assert size == 0, f"Expected size 0 after clear, got {size}"
        print("   ✅ Playlist cleared")
        
        print("\n✅ State management test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ State management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_state_management())
    sys.exit(0 if success else 1)
