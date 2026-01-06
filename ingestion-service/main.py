from fastapi import FastAPI
from pydantic import BaseModel
import requests

from prometheus_client import Gauge, Counter, generate_latest
from fastapi import Response

# prometheus gauge exposing the current size of the ingestion buffer
buffer_gauge = Gauge("ingestion_buffer_size", "Current buffer size")

# counts how many inference requests were triggered
pred_counter = Counter("ingestion_predictions_total", "Total predictions")

# counts how many fog freezing of gait events were detected
fog_counter = Counter("ingestion_fog_total", "FoG predictions")

# fastapi application instance
app = FastAPI(title ="Ingestion service")

# prometheus metrics endpoint
# exposes buffer size and prediction counters for monitoring
@app.get("/metrics")
def metrics():
    buffer_gauge.set(len(buffer))
    return Response(generate_latest(), media_type="text/plain")

# internal buffer
# fixed window size required by the ml model
buffer_size = 128

# sliding buffer that accumulates incoming sensor samples
buffer = []

# stores the most recent prediction result
# used by the carbon controller to make control decisions
last_prediction = None

# internal service url's (docker service names)
anomaly_url = "http://anomaly:8080/predict"
feature_url = "http://feature:8080/extract"


# schema definition for a single imu sample
# enforces correct input structure via validation
class SensorSample(BaseModel):
    AccV: float
    AccML: float
    AccAP: float


# health endpoint queried by the carbon controller
# exposes buffer state and last ml prediction
@app.get("/health")
def health():
    return {
        "ok": True,
        "buffer_size": len(buffer),
        "required": buffer_size,
        "last_prediction": last_prediction
    }

# receives individual sensor samples from the generator service
# buffers samples until a full window is available
@app.post("/ingest")
def ingest(sample: SensorSample):

    # append the incoming sample to the buffer
    buffer.append([sample.AccV, sample.AccML, sample.AccAP])

    # if the buffer is not full yet, do nothing
    if len(buffer) < buffer_size:
        return {
            "ready": False,
            "buffered": len(buffer)
        }
    
    # payload = {
    #     "features": buffer[:buffer_size]
    # }

    # once the buffer reaches the required size
    # prepare a windowed payload for feature extraction
    payload = {
        "window": buffer[:buffer_size]
    }

    # clear the buffer after extracting a full window
    buffer.clear()

    # send it to the feature extractor service for the prediction result
    try:
        response = requests.post(feature_url, json=payload, timeout=3)
        result = response.json()

        # update prediction counters
        pred_counter.inc()
        if result.get("FoG"):
            fog_counter.inc()

        # store the last prediction for external controllers
        last_prediction = result

        print("prediction: ", result)
        return {
            "ready": True,
            "anomaly_response": response.json()
        }
    
    except Exception as e:
        # failure response if downstream services are unavailable
        return {
            "ready": False,
            "error": str(e)
        }
    

