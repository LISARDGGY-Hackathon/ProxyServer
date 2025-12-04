import httpx

"""
Client that sends requests directly to vLLM servers.

It prompts for model (1 or 2), an optional path (default `chat/completions`),
and a prompt. It then POSTs the vLLM-style body directly to the chosen
upstream endpoint and prints the response.
"""

VLLM_1 = "http://210.61.209.139:45014/v1/"
VLLM_2 = "http://210.61.209.139:45005/v1/"
proxy_host = "http://100.68.65.78:8887"

def build_body(prompt: str):
    # Minimal chat-style body compatible with many vLLM endpoints
    return {"messages": [{"role": "user", "content": prompt}]}


def main():
    print("vLLM direct client")

    while True:

        path = input("Path (default: chat/completions): ").strip()
        if not path:
            path = "chat/completions"

        prompt = input("Input prompt: ")

        body = build_body(prompt)

        base = proxy_host

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