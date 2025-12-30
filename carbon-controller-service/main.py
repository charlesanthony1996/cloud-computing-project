from fastapi import FastAPI
import requests
import threading
import time

from prometheus_client import Gauge, Counter,  generate_latest
from fastapi import Response

carbon_rate_gauge = Gauge("carbon_current_rate", "Current carbon-controlled rate")
rate_map = {"low": 1, "medium": 2, "high": 3}


rate_change_counter = Counter("carbon_rate_changes_total", "Number of rate changes")

app = FastAPI(title = "Carbon controller service")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# service urls
# ingestion_url = "http://localhost:8081/health"
# generator_rate_url = "http://localhost:8083/self-rate"

ingestion_url = "http://ingestion:8081/health"
generator_rate_url = "http://generator:8083/self-rate"

# controller config
poll_interval = 5
running = False
last_rate = None

def decide_rate(ingestion_status: dict) -> str:

    # default
    rate = "low"
    
    # example
    if ingestion_status.get("buffer_size", 0) > 100:
        rate = "medium"

    prediction = ingestion_status.get("last_prediction")

    if prediction is not None and prediction.get("FoG") is True:
        rate = "high"

    return rate


def control_loop():
    global last_rate, running

    while running:
        try:
            ingestion_resp = requests.get(ingestion_url, timeout= 2)
            ingestion_status = ingestion_resp.json()

            rate = decide_rate(ingestion_status)

            if rate != last_rate:
                requests.post(generator_rate_url, json={"rate": rate}, timeout = 2)
                carbon_rate_gauge.set(rate_map[rate])
                rate_change_counter.inc()
                last_rate = rate
                print(f"[carbon-controller] rate set to {rate}")
        
        except Exception as e:
            print("[carbon-controller] error", e)
        
        time.sleep(poll_interval)


@app.post("/start")
def start_controller():
    global running

    if not running:
        running = True
        threading.Thread(target=control_loop, daemon = True).start()

    return {"running": True}

@app.post("/stop")
def stop_controller():
    global running

    running = False
    return {"running": True}

@app.get("/status")
def status():
    return {
        "running": running,
        "last_rate": last_rate,
        "poll_interval_rate": poll_interval
    }

