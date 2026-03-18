from app import app
from flask import session
import traceback

print("Testing /my_cases route...")
app.testing = True
app.secret_key = 'test'
client = app.test_client()

with client.session_transaction() as sess:
    sess['logged_in'] = True
    sess['role'] = 'Counsellor'
    sess['full_name'] = 'Mrs. Gertrude Effeh Brew'
    sess['username'] = 'counsellor'

try:
    response = client.get('/my_cases')
    print("STATUS CODE:", response.status_code)
    print("LOCATION IF REDIRECT:", response.location if response.status_code == 302 else "No redirect")
    
    if b'Access restricted' in response.data:
        print("REDIRECT MSG: Access restricted to clinical staff.")
    elif b'Professional profile not found' in response.data:
        print("REDIRECT MSG: Professional profile not found.")
    else:
        print("Data length:", len(response.data))
        
except Exception as e:
    print("APP CRASHED DURING REQUEST!")
    traceback.print_exc()
