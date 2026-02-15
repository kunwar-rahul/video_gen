"""Test the API endpoints."""
import json
import requests
import time

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint."""
    print("\n[1] Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_generate():
    """Test video generation."""
    print("\n[2] Testing /mcp/generate endpoint...")
    
    payload = {
        "prompt": "A beautiful sunset over the ocean with soft waves",
        "duration_target": 30,
        "style": "cinematic",
        "voice": "en-US-neutral",
        "language": "en"
    }
    
    response = requests.post(
        f"{BASE_URL}/mcp/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 202, "Should return 202 Accepted"
    assert "job_id" in data, "Response should contain job_id"
    
    job_id = data["job_id"]
    print(f"✓ Job created with ID: {job_id}")
    
    return job_id


def test_status(job_id):
    """Check job status."""
    print(f"\n[3] Testing /mcp/status/{job_id}...")
    
    response = requests.get(f"{BASE_URL}/mcp/status/{job_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["job_id"] == job_id
    print(f"✓ Status retrieved: {data['status']}")
    
    return data


def test_storyboard(job_id):
    """Get storyboard."""
    print(f"\n[4] Testing /mcp/storyboard/{job_id}...")
    
    response = requests.get(f"{BASE_URL}/mcp/storyboard/{job_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Storyboard available with {len(data.get('scenes', []))} scenes")
        print("✓ Storyboard retrieved")
    else:
        print("Storyboard not yet available (expected for new jobs)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Video Generation Service - API Test")
    print("=" * 60)
    
    try:
        # Test health
        test_health()
        time.sleep(1)
        
        # Generate a video
        job_id = test_generate()
        time.sleep(2)
        
        # Check status
        status_data = test_status(job_id)
        time.sleep(1)
        
        # Get storyboard
        test_storyboard(job_id)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print(f"\nYour first job ID: {job_id}")
        print(f"Check status: curl http://localhost:8080/mcp/status/{job_id}")
        print(f"Get result:  curl http://localhost:8080/mcp/result/{job_id}")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
