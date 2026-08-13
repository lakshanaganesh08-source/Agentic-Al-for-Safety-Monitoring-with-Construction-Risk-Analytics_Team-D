import requests
import json
import time

def test_companion_server():
    print("Testing companion server /chat endpoint on http://localhost:8502/chat...")
    payload = {
        "query": "Hello Apex Builder! Reply in exactly 5 words.",
        "stream": True
    }
    start = time.time()
    try:
        response = requests.post("http://localhost:8502/chat", json=payload, stream=True, timeout=120)
        print("Status code:", response.status_code)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        try:
                            data = json.loads(decoded[6:])
                            chunk = data.get("chunk", "")
                            print(chunk, end="", flush=True)
                        except Exception as e:
                            print(f"\nDecoding failed: {e} for {decoded}")
            print(f"\nCompleted in {time.time() - start:.2f} seconds.")
        else:
            print("Failed:", response.text)
    except Exception as e:
        print("Connection to companion server failed:", str(e))

if __name__ == "__main__":
    test_companion_server()
