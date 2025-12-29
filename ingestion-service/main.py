from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title ="Ingestion service")

# internal buffer
buffer_size = 128
buffer = []
last_prediction = None


anomaly_url = "http://anomaly:8080/predict"
feature_url = "http://feature:8080/extract"

class SensorSample(BaseModel):
    AccV: float
    AccML: float
    AccAP: float


@app.get("/health")
def health():
    return {
        "ok": True,
        "buffer_size": len(buffer),
        "required": buffer_size,
        "last_prediction": last_prediction
    }

@app.post("/ingest")
def ingest(sample: SensorSample):

    buffer.append([sample.AccV, sample.AccML, sample.AccAP])

    if len(buffer) < buffer_size:
        return {
            "ready": False,
            "buffered": len(buffer)
        }
    
    # payload = {
    #     "features": buffer[:buffer_size]
    # }

    payload = {
        "window": buffer[:buffer_size]
    }

    buffer.clear()

    # send it to the anomaly service
    try:
        response = requests.post(feature_url, json=payload, timeout=3)
        result = response.json()
        last_prediction = result

        print("prediction: ", result)
        return {
            "ready": True,
            "anomaly_response": response.json()
        }
    
    except Exception as e:
        return {
            "ready": False,
            "error": str(e)
        }