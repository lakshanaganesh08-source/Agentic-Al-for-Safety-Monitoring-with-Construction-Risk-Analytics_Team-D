import requests
import json
import time

def test_stream_connection():
    print("Testing streaming response from local Ollama on http://localhost:11434/api/chat...")
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "user", "content": "Write a 3-sentence welcome message for a construction company."}
        ],
        "stream": True,
        "options": {
            "temperature": 0.3
        }
    }
    start = time.time()
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, stream=True, timeout=120)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        chunk = data.get("message", {}).get("content", "")
                        print(chunk, end="", flush=True)
                    except Exception as e:
                        print(f"\nError decoding JSON line: {e} ({decoded})")
            print(f"\nStream finished. (took {time.time() - start:.2f} seconds)")
        else:
            print("Error response:", response.text)
    except Exception as e:
        print(f"\nConnection failed: {str(e)}")

if __name__ == "__main__":
    test_stream_connection()
