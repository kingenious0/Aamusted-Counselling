import requests

urls = [
    "https://aamusted-counselling-cloud-bridge.vercel.app/push",
    "https://aamusted-counselling-cloud-bridge.vercel.app/api/push",
    "https://aamusted-counselling-cloud-bridge.vercel.app/sync/push"
]

for url in urls:
    try:
        print(f"Testing POST {url}...")
        resp = requests.post(url, timeout=10)
        print(f"Response: {resp.status_code}")
        # print(f"Body: {resp.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

print("\nTesting GET root...")
try:
    resp = requests.get("https://aamusted-counselling-cloud-bridge.vercel.app/", timeout=10)
    print(f"Root GET Response: {resp.status_code}")
except Exception as e:
    print(f"Root GET Error: {e}")
