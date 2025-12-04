import httpx

"""
Client that sends requests directly to vLLM servers.

It prompts for model (1 or 2), an optional path (default `chat/completions`),
and a prompt. It then POSTs the vLLM-style body directly to the chosen
upstream endpoint and prints the response.
"""

VLLM_1 = "http://210.61.209.139:45014/v1/"
VLLM_2 = "http://210.61.209.139:45005/v1/"


def build_body(prompt: str):
    # Minimal chat-style body compatible with many vLLM endpoints
    return {"messages": [{"role": "user", "content": prompt}]}


def main():
    print("vLLM direct client")

    while True:
        model = input("Select model (1 or 2) or 'exit': ")
        if model == "exit":
            break
        if model not in ("1", "2"):
            print("Invalid model number. Please enter 1 or 2.\n")
            continue

        path = input("Path (default: chat/completions): ").strip()
        if not path:
            path = "chat/completions"

        prompt = input("Input prompt: ")

        body = build_body(prompt)

        if model == "1":
            base = VLLM_1
        else:
            base = VLLM_2

        url = base.rstrip("/") + "/" + path.lstrip("/")

        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(url, json=body, headers={"Content-Type": "application/json"})
        except httpx.RequestError as e:
            print("Request error:", e)
            continue

        print(f"Upstream URL: {url}  Status: {resp.status_code}")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)

        print()


if __name__ == "__main__":
    main()