import requests

url = "http://127.0.0.1:8001/upload"
files = {'file': open('test_upload.txt', 'rb')}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
