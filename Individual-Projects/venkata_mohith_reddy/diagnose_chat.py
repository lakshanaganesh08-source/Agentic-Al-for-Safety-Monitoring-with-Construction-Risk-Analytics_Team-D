import sys
import os
import json
import time
import requests

def run_diagnostics():
    print("==================================================")
    print("DIAGNOSE_CHAT.PY — CHATBOT DIAGNOSTIC SUITE")
    print("==================================================")
    
    # 1. Test ollama_helper module
    try:
        import ollama_helper
        print("[CHECK 1] Importing ollama_helper... SUCCESS")
    except Exception as e:
        print(f"[CHECK 1] Importing ollama_helper... FAILED: {e}")
        return

    # 2. Test check_connection()
    conn_ok, conn_err = ollama_helper.check_connection()
    if conn_ok:
        print("[CHECK 2] ollama_helper.check_connection()... PASS")
    else:
        print(f"[CHECK 2] ollama_helper.check_connection()... FAIL: {conn_err}")

    # 3. Test check_model()
    model_ok, model_err = ollama_helper.check_model('llama3.2')
    if model_ok:
        print("[CHECK 3] ollama_helper.check_model('llama3.2')... PASS")
    else:
        print(f"[CHECK 3] ollama_helper.check_model('llama3.2')... FAIL: {model_err}")

    # 4. Test send_prompt()
    resp, send_err = ollama_helper.send_prompt("Hello! Reply with 'System Operational' in 2 words.", temperature=0.1)
    if not send_err and resp:
        print(f"[CHECK 4] ollama_helper.send_prompt()... PASS (Response: {repr(resp.strip())})")
    else:
        print(f"[CHECK 4] ollama_helper.send_prompt()... FAIL: {send_err}")

    # 5. Test background port & server endpoint
    port = 8502
    if os.path.exists("templates/port.json"):
        try:
            with open("templates/port.json", "r") as f:
                port_data = json.load(f)
                port = port_data.get("port", 8502)
        except Exception:
            pass
    print(f"[CHECK 5] Checking active companion API port: {port}")
    try:
        url = f"http://127.0.0.1:{port}/chat"
        r = requests.post(url, json={"query": "Diagnostic ping", "stream": False}, timeout=45)
        if r.status_code == 200:
            data = r.json()
            if "response" in data and data["response"]:
                print(f"[CHECK 5] Endpoint {url}... PASS (Response: {repr(data['response'][:60])})")
            else:
                print(f"[CHECK 5] Endpoint {url}... FAIL: Missing response field in JSON {data}")
        else:
            print(f"[CHECK 5] Endpoint {url}... FAIL: HTTP status {r.status_code}")
    except Exception as e:
        print(f"[CHECK 5] Endpoint http://127.0.0.1:{port}/chat... FAIL: {e}")

    print("==================================================")
    print("DIAGNOSTICS COMPLETED.")
    print("==================================================")

if __name__ == "__main__":
    run_diagnostics()
