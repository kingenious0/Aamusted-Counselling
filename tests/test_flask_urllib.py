import urllib.request
import urllib.error

print("Testing Flask application using urllib...")

try:
    # Make a request to the create_session endpoint
    print("1. Testing create_session endpoint...")
    response = urllib.request.urlopen('http://127.0.0.1:5000/create_session', timeout=10)
    
    print(f"   Response status: {response.status}")
    if response.status == 200:
        print("   ✓ Request successful!")
        content = response.read().decode('utf-8')
        print(f"   Response length: {len(content)} characters")
        if "sqlite3.OperationalError" in content:
            print("   ✗ ERROR DETECTED IN RESPONSE!")
            # Find the error in the content
            error_start = content.find("sqlite3.OperationalError")
            if error_start != -1:
                error_end = content.find("\n", error_start)
                if error_end == -1:
                    error_end = error_start + 500
                error_msg = content[error_start:error_end]
                print(f"   Error: {error_msg}")
        else:
            print("   ✓ No error detected in response")
    else:
        print(f"   ✗ Request failed with status {response.status}")
        
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error: {e.code} - {e.reason}")
    if e.code == 500:
        error_content = e.read().decode('utf-8')
        print(f"   Error content: {error_content[:500]}...")
except urllib.error.URLError as e:
    print(f"   ✗ Could not connect to Flask application: {e}")
    print("   Make sure Flask is running on http://127.0.0.1:5000")
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")

print("\nDirect testing complete.")