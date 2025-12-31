from fastapi import FastAPI, Body
import numpy as np
import requests
import os

# fastapi application instance
app = FastAPI(title="Feature extractor service")

# url of the anomaly detection service
# read from the environment variable if provided
# fallback uses docker service name -> "anomaly"
# this keeps it portable nd configurable
anomaly_url = os.getenv(
    "anomaly_url",
    "http://anomaly:8080/predict"
)

# reuiqred window time length -> matches model input
seq_len = 128

# number of sensor axes from a single IMU
n_features = 3

# utility function to normalize a time window
def normalize(x: np.ndarray) -> np.ndarray:

    # compute mean and std per axis
    mean = x.mean(axis = 0, keepdims=True)

    # small epsilon avoids division by zero
    std = x.std(axis = 0, keepdims=True) + 1e-6

    # returns normalized feature matrix
    return (x - mean) / std

# health check endpoint
# confirms that the service is alive
@app.get("/health")
def health():
    return {"ok": True, "service": "feature-extractor"}

# receives a json payload from the ingestion service
@app.post("/extract")
def extract(payload: dict = Body(...)):

    # convert incoming list to a numpy array
    # ensures numeric consistency and fast computation
    raw = np.array(payload["window"], dtype=np.float32)

    # input validation -> must be 2D and must have exactly 3 sensor axes
    # other inputs do not reach the model because of this check
    if raw.ndim != 2 or raw.shape[1] != 3:
        return {"error": "window must be n x 3 array"}
    
    # enforce fixed window size
    # if there are too many samples, truncate it to the limit of the sequence length
    if raw.shape[0] > 128:
        raw = raw[:128]

    # if there are too few samples, pad it with zeros at the end
    # this keeps input shape consistent
    elif raw.shape[0] < 128:
        pad = np.zeros((128 - raw.shape[0], 3), dtype=np.float32)

        raw = np.vstack((raw, pad))

    # features = normalize(raw)
    # normalize only
    # makes features scale invariant
    mean = raw.mean(axis=0, keepdims=True)
    std = raw.std(axis = 0, keepdims=True) + 1e-6
    norm = (raw - mean) / std


    # forward it to the anomaly service
    # converts the numpy array into a json serializable list
    # the timeout avoids blocking if the anomaly service fails
    resp = requests.post(
        anomaly_url,
        json={"features": norm.tolist()},
        timeout=5
    )

    return resp.json()
