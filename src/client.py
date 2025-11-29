import httpx

"""
Simple HTTP client to talk to the new FastAPI proxy.
It sends a JSON body with `model` and `input` and prints the JSON response.

Run: `python src/client.py` and follow prompts.
"""

PROXY_HOST = "127.0.0.1"  # change to proxy host if needed
PROXY_PORT = 5678

BASE_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"


def main():
    print(f"Proxy client will POST to {BASE_URL}/predict")

    while True:
        model = input("Select model (1 or 2) or 'exit': ")
        if model == "exit":
            break
        if model not in ("1", "2"):
            print("Invalid model number. Please enter 1 or 2.\n")
            continue

        prompt = input("Input prompt: ")

        # Build a minimal vLLM-style body. Many vLLM servers accept a `messages` list like OpenAI Chat API.
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{BASE_URL}/predict", json=payload)
        except httpx.RequestError as e:
            print("Request error:", e)
            continue

        try:
            data = resp.json()
            print("Response (JSON):")
            print(data)
        except Exception:
            print("Response (text):")
            print(resp.text)

        print()


if __name__ == "__main__":
    main()