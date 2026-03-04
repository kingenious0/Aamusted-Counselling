import requests
import os

# Test the Flask application directly
print("Testing Flask application directly...")

try:
    # Make a request to the create_session endpoint
    print("1. Testing create_session endpoint...")
    response = requests.get('http://127.0.0.1:5000/create_session', timeout=10)
    print(f"   Response status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Request successful!")
        print(f"   Response length: {len(response.text)} characters")
    else:
        print(f"   ✗ Request failed with status {response.status_code}")
        if response.status_code == 500:
            print(f"   Error response: {response.text[:500]}...")
        
except requests.exceptions.RequestException as e:
    print(f"   ✗ Could not connect to Flask application: {e}")
    print("   Make sure Flask is running on http://127.0.0.1:5000")

print("\nDirect testing complete.")