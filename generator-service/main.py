from fastapi import FastAPI
import random
import time
import threading
import requests

app = FastAPI(title="Data generator service")

ingest_url = "http://ingestion:8081/ingest"

rates = {
    # 1 sample a second
    "low": 1,
    "medium": 5,
    "high": 10
}

running = False
current_rate = "low"

def generate_loop():
    global running

    while running:
        payload = {
            "AccV": random.uniform(-1.0, 1.0),
            "AccML": random.uniform(-1.0, 1.0),
            "AccAP": random.uniform(-1.0, 1.0)
        }

        try:
            requests.post(ingest_url, json=payload, timeout = 1)
        except Exception as e:
            print("send failed: ", e)

        time.sleep(1 / rates[current_rate])

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


@app.post("/stop")
def stop():
    global running

    running = False
    return {
        "running": False
    }

@app.post("/self-rate")
def set_rate(body: dict):
    global current_rate

    rate = body.get("rate")

    if rate not in rates:
        return { "error": "rate must be low | medium | high"}
    
    current_rate = rate
    return { "rate": current_rate }

@app.get("/status")
def status():
    return {
        "running": running,
        "rate": current_rate,
        "samples_per_second": rates[current_rate]
    }
     