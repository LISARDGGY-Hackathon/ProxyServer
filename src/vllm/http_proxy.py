"""
Minimal HTTP reverse proxy (pure forwarder).

This proxy does NOT perform model selection or add extra logic — it simply
forwards incoming HTTP requests (method, path, query, headers, body) to a single
upstream base URL and returns the upstream response.

Configure the upstream via the `UPSTREAM_URL` environment variable. If not set,
the default is `http://210.61.209.139:45014/v1/`.
"""

import os
from fastapi import FastAPI, Request, Response
import httpx
import asyncio

UPSTREAM_URL1 = os.getenv("UPSTREAM_URL1", "http://210.61.209.139:45014/v1/")
UPSTREAM_URL2 = os.getenv("UPSTREAM_URL2", "http://210.61.209.139:45005/v1/")

app = FastAPI()


_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def _filter_request_headers(headers):
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP and k.lower() != "host"}


def _filter_response_headers(headers):
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def forward(path: str, request: Request):
    # Build target URL by appending the incoming path and preserving query params
    upstream1 = UPSTREAM_URL1.rstrip("/") + "/" + path.lstrip("/")
    upstream2 = UPSTREAM_URL2.rstrip("/") + "/" + path.lstrip("/")
    params = dict(request.query_params)

    req_headers = _filter_request_headers(dict(request.headers))
    body = await request.body()
    
    async def fetch(url):
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                params=params,
                headers=req_headers,
                content=body,
            )
        if resp.status_code >= 500:
            raise httpx.RequestError(f"Server returned {resp.status_code}")
        return resp

    tasks = [
        asyncio.create_task(fetch(upstream1), name="Model 1"),
        asyncio.create_task(fetch(upstream2), name="Model 2")
    ]
    
    final_resp = None
    pending = set(tasks)
    while(pending):
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        
        for task in done:
            try:
                result = task.result()
                final_resp = result
                
                for p in pending:
                    p.cancel()
                
                pending = set()
                break
            except (httpx.RequestError, asyncio.CancelledError) as e:
                print(f"One upstream failed: {e}. Waiting for others...")
                pass
    
    if(final_resp is None):
        return Response(content="Error: All upstreams failed.", status_code=502)
    
    resp_headers = _filter_response_headers(dict(final_resp.headers))
    return Response(content=final_resp.content, status_code=final_resp.status_code, headers=resp_headers)