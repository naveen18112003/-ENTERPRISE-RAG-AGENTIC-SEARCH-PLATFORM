import requests

url = "http://127.0.0.1:8001/search"
payload = {
    "query": "Compare test file with nothing",
    "mode": "agentic"
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
