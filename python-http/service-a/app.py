from flask import Flask, g, jsonify, request
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
app = Flask(__name__)


@app.before_request
def start_request_timer():
    g.request_start = time.perf_counter()


@app.after_request
def log_request(response):
    latency_ms = (time.perf_counter() - g.request_start) * 1000
    logging.info(
        "service=A endpoint=%s status=%s latency_ms=%.2f",
        request.path,
        response.status_code,
        latency_ms,
    )
    return response

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/echo")
def echo():
    msg = request.args.get("msg", "")
    return jsonify(echo=msg)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
