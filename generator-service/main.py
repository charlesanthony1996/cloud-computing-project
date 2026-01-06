from fastapi import FastAPI
import random
import time
import threading
import requests

from prometheus_client import Gauge, generate_latest
from fastapi import Response

# prometheus gauge that exposes the current data generation rate
# this allows monitoring how aggresively data is being produced
rate_gauge = Gauge("generator_rate", "Current generator rate")

# fast api application instance
app = FastAPI(title="Data generator service")

# ingestion service endpoint (internal docker dns name)
# generated sensor samples are sent here 
ingest_url = "http://ingestion:8081/ingest"

# mapping from symbolic rate levels to sample second 
# these rates are dynamically controlled by the carbon controller
rates = {
    # 1 sample a second
    # energy saving mode
    "low": 1,
    # balanced mode
    "medium": 5,
    # perfomance mode
    "high": 10
}

# controls whether the generator loop is active
running = False

# currently active generation rate
current_rate = "low"

# this functions continuously generates synthetic imu data 
# and sends it to the ingestion service at the selected rate
def generate_loop():
    global running

    while running:
        # simulated 3 axis aceelerometer sample
        payload = {
            "AccV": random.uniform(-1.0, 1.0),
            "AccML": random.uniform(-1.0, 1.0),
            "AccAP": random.uniform(-1.0, 1.0)
        }

        # send the sample to the ingestion service
        # timeout prevents blocking if ingestion becomes unavailable

        try:
            requests.post(ingest_url, json=payload, timeout = 1)
        except Exception as e:
            print("send failed: ", e)

        # sleep duration depends on the current rate
        # higher rate -> shorter sleep -> more samples per second
        time.sleep(1 / rates[current_rate])

# starts the data generator
# so that the api stays responsive
@app.post("/start")
def start():
    global running
    if not running:
        running = True
        threading.Thread(target = generate_loop, daemon=True).start()


    return {
        "running": True,
        "rate": current_rate
    }

# stops the data generator
# the background loop stops as running is set to False
@app.post("/stop")
def stop():
    global running

    running = False
    return {
        "running": False
    }

# allows external services (ex:- carbon controller service)
# to dynamically change the data generation rate
@app.post("/self-rate")
def set_rate(body: dict):
    global current_rate

    rate = body.get("rate")

    # validate the requested rate
    if rate not in rates:
        return { "error": "rate must be low | medium | high"}
    
    current_rate = rate
    return { "rate": current_rate }

# returns the current operational status of the generator
# useful for debugging and demo purposes
@app.get("/status")
def status():
    return {
        "running": running,
        "rate": current_rate,
        "samples_per_second": rates[current_rate]
    }

# prometheus metrics endpoint
# exposes the current data generation rate as a numeric gauge
@app.get("/metrics")
def metrics():
    rate_gauge.set(rates[current_rate])
    return Response(generate_latest(), media_type="text/plain")

