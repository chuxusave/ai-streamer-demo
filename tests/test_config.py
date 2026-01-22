"""Test configuration loading."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_loads():
    """Test that configuration can be loaded."""
    try:
        from config import settings
        print(f"✅ Config loaded successfully")
        print(f"   - DashScope API Key: {'*' * 20 if settings.dashscope_api_key else 'NOT SET'}")
        print(f"   - Host: {settings.host}")
        print(f"   - Port: {settings.port}")
        return True
    except Exception as e:
        print(f"❌ Config load failed: {e}")
        return False

if __name__ == "__main__":
    success = test_config_loads()
    sys.exit(0 if success else 1)
