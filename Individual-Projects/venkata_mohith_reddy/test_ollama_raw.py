import requests
import json
import time

def test_raw_connection():
    print("Sending test request to local Ollama on http://localhost:11434/api/chat with a 120-second timeout...")
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "user", "content": "Hello! Reply with exactly 'Ollama Connection is Working' and nothing else."}
        ],
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    start = time.time()
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        elapsed = time.time() - start
        if response.status_code == 200:
            result = response.json()
            reply = result.get("message", {}).get("content", "")
            print(f"Response status: 200 (took {elapsed:.2f} seconds)")
            print("Response content:", reply.strip())
        else:
            print(f"Error: Status code {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"Connection failed: {str(e)}")

if __name__ == "__main__":
    test_raw_connection()
