vllm_gpt_oss_120b_1="http://210.61.209.139:45014/v1/"
vllm_gpt_oss_120b_2="http://210.61.209.139:45005/v1/"
"""
HTTP proxy for forwarding requests to different vLLM endpoints.

Usage:
- Start server: `uvicorn src.proxy_server:app --host 0.0.0.0 --port 8888`
- POST to `/predict` with JSON {"model":"1" or "2", "input": {...}}
  The proxy forwards the JSON `input` to the selected vLLM server's
  `chat/completions` endpoint by default and returns the vLLM response.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import logging

vllm_gpt_oss_120b_1 = "http://210.61.209.139:45014/v1/"
vllm_gpt_oss_120b_2 = "http://210.61.209.139:45005/v1/"

app = FastAPI()
logger = logging.getLogger("proxy")
logging.basicConfig(level=logging.INFO)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(request: Request):
    """Accepts JSON payload with keys:
    - model: "1" or "2"
    - input: JSON body to forward to vLLM server
    Optionally: path: path to append to base vLLM url (default: "chat/completions").
    """
    body = await request.json()
    model_num = str(body.get("model", ""))
    input_payload = body.get("input")
    path = body.get("path", "chat/completions")

    if not input_payload:
        raise HTTPException(status_code=400, detail="Missing 'input' in request body")

    if model_num == "1":
        base = vllm_gpt_oss_120b_1
    elif model_num == "2":
        base = vllm_gpt_oss_120b_2
    else:
        raise HTTPException(status_code=400, detail="Unknown model number, must be '1' or '2'")

    # Build target URL. base already ends with /v1/ in our config.
    url = base.rstrip("/") + "/" + path.lstrip("/")

    logger.info(f"Forwarding request to {url}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=input_payload)
    except httpx.RequestError as e:
        logger.exception("Error forwarding request")
        raise HTTPException(status_code=502, detail=str(e))

    # Try to return JSON if possible, otherwise raw text
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    else:
        return JSONResponse(status_code=resp.status_code, content={"text": resp.text})
