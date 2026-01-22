"""Test API endpoints."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

def test_api_endpoints():
    """Test API endpoints."""
    print("\n" + "="*60)
    print("🧪 Testing API Endpoints")
    print("="*60)
    
    client = TestClient(app)
    
    try:
        # Test root endpoint
        print("📡 Testing root endpoint...")
        resp = client.get("/")
        assert resp.status_code in [200, 307], f"Expected 200 or 307, got {resp.status_code}"
        print(f"   ✅ Root endpoint: {resp.status_code}")
        
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        resp = client.get("/health")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "status" in data, "Missing status in response"
        print(f"   ✅ Health endpoint: {data}")
        
        # Test status endpoint
        print("📊 Testing status endpoint...")
        resp = client.get("/api/status")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "is_streaming" in data, "Missing is_streaming in response"
        print(f"   ✅ Status endpoint: {data}")
        
        print("\n✅ API endpoints test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
