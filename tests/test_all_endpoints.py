import urllib.request
import urllib.error

print("Testing various Flask endpoints...")

endpoints = [
    '/',
    '/dashboard',
    '/create_session',
    '/sessions',
    '/students',
    '/manage_appointments'
]

for endpoint in endpoints:
    try:
        print(f"\nTesting {endpoint}...")
        response = urllib.request.urlopen(f'http://127.0.0.1:5000{endpoint}', timeout=10)
        
        if response.status == 200:
            content = response.read().decode('utf-8')
            if "sqlite3.OperationalError" in content:
                print(f"   ✗ ERROR DETECTED in {endpoint}!")
                # Find the error in the content
                error_start = content.find("sqlite3.OperationalError")
                if error_start != -1:
                    error_end = content.find("\n", error_start)
                    if error_end == -1:
                        error_end = error_start + 200
                    error_msg = content[error_start:error_end]
                    print(f"   Error: {error_msg}")
            else:
                print(f"   ✓ {endpoint} - OK (200)")
        else:
            print(f"   ? {endpoint} - Status {response.status}")
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   ? {endpoint} - Not found (404)")
        elif e.code == 500:
            print(f"   ✗ {endpoint} - Server error (500)")
            error_content = e.read().decode('utf-8')
            if "sqlite3.OperationalError" in error_content:
                error_start = error_content.find("sqlite3.OperationalError")
                error_end = error_content.find("\n", error_start)
                if error_end == -1:
                    error_end = error_start + 200
                error_msg = error_content[error_start:error_end]
                print(f"   Error: {error_msg}")
        else:
            print(f"   ? {endpoint} - HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"   ? {endpoint} - Error: {e}")

print("\nEndpoint testing complete.")