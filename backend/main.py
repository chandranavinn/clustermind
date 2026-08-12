from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = FastAPI(title="Backend")

REQUEST_COUNT = Counter(
    "backend_http_requests_total", "Total HTTP requests", ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "backend_http_request_duration_seconds", "Request latency", ["endpoint", "method"]
)


def track(endpoint: str, method: str, status: str, start: float):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(time.time() - start)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)


@app.get("/api/hello")
async def hello():
    start = time.time()
    result = {"message": "Hello from backend!"}
    track("/api/hello", "GET", "200", start)
    return result


@app.get("/api/add")
async def add(a: int = 1, b: int = 2):
    start = time.time()
    result = {"a": a, "b": b, "sum": a + b}
    track("/api/add", "GET", "200", start)
    return result
