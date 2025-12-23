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

    if raw.ndim != 2 or raw.shape[1] != n_features:
        return {"error": "window must be n x 3 array"}
    

    if raw.shape[0] > seq_len:
        raw = raw[:seq_len]

    elif raw.shape[0] < seq_len:
        pad = np.zeros((seq_len - raw.shape[0], n_features), dtype=np.float32)

        raw = np.vstack((raw, pad))

    features = normalize(raw)


    # forward it to the anomaly service
    resp = requests.post(
        anomaly_url,
        json={"features": features.tolist()},
        timeout=5
    )

    return resp.json()
