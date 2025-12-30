from fastapi import FastAPI
import requests
import threading
import time

# prometheus metric imports
from prometheus_client import Gauge, Counter,  generate_latest
from fastapi import Response

# gauge -> a value that goes up and down
# we expose the current rate selected by the carbon controller
carbon_rate_gauge = Gauge("carbon_current_rate", "Current carbon-controlled rate")

# mapping the string rate -> numeric value
# promoetheus gauges must be numeric
rate_map = {"low": 1, "medium": 2, "high": 3}

# counter -> monotonically increasing value
# counts how many times the controller changed the rate
rate_change_counter = Counter("carbon_rate_changes_total", "Number of rate changes")

# fast api app instancing
app = FastAPI(title = "Carbon controller service")

@app.get("/metrics")
def metrics():
    # prometheus scrapes this endpoint
    # generate_latest() returns all registered metrics
    return Response(generate_latest(), media_type="text/plain")

# service urls for local testing only
# ingestion_url = "http://localhost:8081/health"
# generator_rate_url = "http://localhost:8083/self-rate"

# docker compose creates an internal DNS
# ingestion and generator containers are service names
ingestion_url = "http://ingestion:8081/health"
generator_rate_url = "http://generator:8083/self-rate"

# controller config
# seconds between checks
poll_interval = 5

# controls the background loop
running = False

# last applied rate (prevents sampling generator)
last_rate = None

def decide_rate(ingestion_status: dict) -> str:

    # default safe behaviour
    rate = "low"
    
    # buffer pressuree
    # ingestion buffer is filling up
    # generator is producing too fast
    # we slow things down slightly -> switches to medium
    if ingestion_status.get("buffer_size", 0) > 100:
        rate = "medium"

    # ml prediction (FoG or no FoG)
    prediction = ingestion_status.get("last_prediction")

    # system increases sampling frequency
    # more data = higher diagnostic resolution
    if prediction is not None and prediction.get("FoG") is True:
        rate = "high"

    return rate

# this runs asynchronously -> not blocking fastAPI
# loop runs until /stop is called
def control_loop():
    global last_rate, running

    while running:
        # query ingestion health
        # pulls buffer size, last ML prediction, readiness state
        try:
            ingestion_resp = requests.get(ingestion_url, timeout= 2)
            ingestion_status = ingestion_resp.json()

            # decide the new rate
            rate = decide_rate(ingestion_status)

            # apply the rate only if changed
            # this prevents unnecessary HTTP calls
            # metric spam
            # unstable control oscillations
            if rate != last_rate:

                # tell generator to switch the rate
                requests.post(generator_rate_url, json={"rate": rate}, timeout = 2)

                # update the metrics
                carbon_rate_gauge.set(rate_map[rate])
                rate_change_counter.inc()
                last_rate = rate
                print(f"[carbon-controller] rate set to {rate}")
        
        except Exception as e:
            print("[carbon-controller] error", e)
        
        # sleep until the next poll
        time.sleep(poll_interval)

# start the carbon controller service
@app.post("/start")
def start_controller():
    global running

    if not running:
        running = True
        threading.Thread(target=control_loop, daemon = True).start()

    return {"running": True}

# stop the carbon controller service
@app.post("/stop")
def stop_controller():
    global running

    running = False
    return {"running": True}

# status endpoint is useful for debugging, demos
@app.get("/status")
def status():
    return {
        "running": running,
        "last_rate": last_rate,
        "poll_interval_rate": poll_interval
    }

