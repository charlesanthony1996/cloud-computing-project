from fastapi import FastAPI, Body
import numpy as np
import requests
import os

app = FastAPI(title="Feature extractor service")

anomaly_url = os.getenv(
    "anomaly_url",
    "http://anomaly:8080/predict"
)

seq_len = 128
n_features = 3

def normalize(x: np.ndarray) -> np.ndarray:

    mean = x.mean(axis = 0, keepdims=True)
    std = x.std(axis = 0, keepdims=True) + 1e-6
    return (x - mean) / std


@app.get("/health")
def health():
    return {"ok": True, "service": "feature-extractor"}

@app.post("/extract")
def extract(payload: dict = Body(...)):

    raw = np.array(payload["window"], dtype=np.float32)

    if raw.ndim != 2 or raw.shape[1] != 3:
        return {"error": "window must be n x 3 array"}
    

    if raw.shape[0] > 128:
        raw = raw[:128]

    elif raw.shape[0] < 128:
        pad = np.zeros((128 - raw.shape[0], 3), dtype=np.float32)

        raw = np.vstack((raw, pad))

    # features = normalize(raw)
    # normalize only
    mean = raw.mean(axis=0, keepdims=True)
    std = raw.std(axis = 0, keepdims=True) + 1e-6
    norm = (raw - mean) / std


    # forward it to the anomaly service
    resp = requests.post(
        anomaly_url,
        json={"features": norm.tolist()},
        timeout=5
    )

    return resp.json()
