from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title ="Ingestion service")

# internal buffer
buffer_size = 128
buffer = []


anomaly_url = "http://anomaly:8080/predict"

class SensorSample(BaseModel):
    AccV: float
    AccML: float
    AccAP: float


@app.get("/health")
def health():
    return {
        "ok": True,
        "buffer_size": len(buffer),
        "required": buffer_size
    }

@app.post("/ingest")
def ingest(sample: SensorSample):

    buffer.append([sample.AccV, sample.AccML, sample.AccAP])

    if len(buffer) < buffer_size:
        return {
            "ready": False,
            "buffered": len(buffer)
        }
    
    payload = {
        "features": buffer[:buffer_size]
    }

    buffer.clear()

    # send it to the anomaly service
    try:
        response = requests.post(anomaly_url, json=payload, timeout=3)
        return {
            "ready": True,
            "anomaly_response": response.json()
        }
    
    except Exception as e:
        return {
            "ready": False,
            "error": str(e)
        }