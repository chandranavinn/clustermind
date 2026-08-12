import os
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

app = FastAPI(title="Frontend")

REQUEST_COUNT = Counter(
    "frontend_http_requests_total", "Total HTTP requests", ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "frontend_http_request_duration_seconds", "Request latency", ["endpoint", "method"]
)


def track(endpoint: str, method: str, status: str, start: float):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(time.time() - start)


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ClusterMind v2 Demo</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 2rem;
            background-color: #0f172a;  /* dark slate blue */
            color: #e5e7eb;             /* light gray text */
        }
        h1 {
            color: #38bdf8;             /* cyan accent */
        }
        p {
            color: #e5e7eb;
        }
        button {
            padding: 0.5rem 1rem;
            margin-right: 1rem;
            border: none;
            border-radius: 4px;
            background-color: #22c55e;
            color: #0f172a;
            cursor: pointer;
        }
        button:hover {
            background-color: #16a34a;
        }
        #result {
            margin-top: 1rem;
            padding: 1rem;
            border: 1px solid #374151;
            background-color: #020617;
            white-space: pre;
        }
    </style>
</head>
<body>
    <h1>ClusterMind v2 Demo</h1>
    <p>Frontend calling backend API inside Kubernetes.</p>
    <button onclick="callHello()">Call /api/hello</button>
    <button onclick="callAdd()">Call /api/add</button>
    <div id="result">Click a button to see the backend response.</div>

    <script>
    async function callHello() {
        const res = await fetch('/call-backend');
        document.getElementById('result').innerText = await res.text();
    }
    async function callAdd() {
        const res = await fetch('/add?a=3&b=9');
        document.getElementById('result').innerText = await res.text();
    }
    </script>
</body>
</html>
"""


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)


@app.get("/", response_class=HTMLResponse)
async def index():
    start = time.time()
    track("/", "GET", "200", start)
    return HTML_PAGE


@app.get("/call-backend")
async def call_backend():
    start = time.time()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}/api/hello", timeout=5.0)
    track("/call-backend", "GET", str(resp.status_code), start)
    return JSONResponse(resp.json())


@app.get("/add")
async def call_add(a: int = 1, b: int = 2):
    start = time.time()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}/api/add", params={"a": a, "b": b}, timeout=5.0)
    track("/add", "GET", str(resp.status_code), start)
    return JSONResponse(resp.json())
