from flask import Flask, g, jsonify, request
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
app = Flask(__name__)

SERVICE_A = "http://127.0.0.1:8080"
SERVICE_A_TIMEOUT_SECONDS = 1.0


@app.before_request
def start_request_timer():
    g.request_start = time.perf_counter()


@app.after_request
def log_request(response):
    latency_ms = (time.perf_counter() - g.request_start) * 1000
    logging.info(
        "service=B endpoint=%s status=%s latency_ms=%.2f",
        request.path,
        response.status_code,
        latency_ms,
    )
    return response

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    msg = request.args.get("msg", "")
    try:
        r = requests.get(
            f"{SERVICE_A}/echo",
            params={"msg": msg},
            timeout=SERVICE_A_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
        return jsonify(service_b="ok", service_a=data)
    except (requests.RequestException, ValueError) as error:
        logging.error(
            'service=B dependency=service-A error="%s"',
            error,
        )
        return jsonify(
            service_b="ok",
            service_a="unavailable",
            error=str(error),
        ), 503

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081)
