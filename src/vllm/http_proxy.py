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
    upstream = UPSTREAM_URL.rstrip("/") + "/" + path.lstrip("/")
    params = dict(request.query_params)

    req_headers = _filter_request_headers(dict(request.headers))
    body = await request.body()

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.request(
            method=request.method,
            url=upstream,
            params=params,
            headers=req_headers,
            content=body,
        )

    resp_headers = _filter_response_headers(dict(resp.headers))
    return Response(content=resp.content, status_code=resp.status_code, headers=resp_headers)

