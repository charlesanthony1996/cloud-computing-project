from fastapi import FastAPI, Body, Response
import torch
import os
import numpy as np
from model_lstm import SimpleLstm, train_lstm, LightLstm
from codecarbon import EmissionsTracker

from prometheus_client import Gauge, generate_latest


app = FastAPI(title="Anomaly service - lstm trainer & inference")

model_path = "lstm_model.pt"
# train_folder = "/app/train/defog/train"
train_folder = "/app/train"

# default mode
MODE = "performance"

inference_mode = Gauge("inference_mode", "0=eco, 1=performance")

# load the models
if not os.path.exists("simple_lstm_model.pt"):
    raise RuntimeError("simple model not found")

if not os.path.exists("light_lstm_model.pt"):
    raise RuntimeError("light model not found")


simple_model = SimpleLstm(input_size=3)
simple_model.load_state_dict(torch.load("simple_lstm_model.pt", map_location="cpu"))
simple_model.eval()

light_model = LightLstm(input_size=3)
light_model.load_state_dict(torch.load("light_lstm_model.pt", map_location="cpu"))
light_model.eval()

# if os.path.exists("simple_lstm_model.pt"):
#     simple_model.load_state_dict(torch.load("simple_lstm_model.pt", map_location="cpu"))
# else:
#     raise RuntimeError("simple_lstm_model.pt not found")

# if os.path.exists("light_lstm_model.pt"):
#     light_model.load_state_dict(torch.load())

# train if missing
# if not os.path.exists(model_path):
#     print("training model since lstm_model.pt not found")
#     model = train_lstm(train_folder)

# else:
#     model = SimpleLstm()
#     model.load_state_dict(torch.load(model_path, map_location= torch.device("cpu")))
#     print("loaded existing model from lstm_model.pt")

# model.eval()

@app.get("/health")
def health():
    return {"ok": True, "mode": MODE, "models_loaded": True}
    # return { "ok": True, "model": "SimpleLSTM", "trained": os.path.exists(model_path)}

@app.post("/predict")
def predict(payload: dict = Body(...)):

    tracker = EmissionsTracker(
        project_name="fog-inference",
        measure_power_specs=1,
        log_level="error"
    )

    tracker.start()

    try:
        arr = np.array(payload["features"], dtype=np.float32)

        # validate: must be (n, 3)
        if arr.ndim != 2 or arr.shape[1] != 3:
            return {"error": "features must be list of [AccV, AccML, AccAP] triplets"}
        
        # zero pad or truncate to exactly 128 steps
        if arr.shape[0] >= 128:
            arr = arr[:128]

        else:
            padding = np.zeros((128 - arr.shape[0], 3), dtype=np.float32)
            arr = np.vstack((arr, padding))

        x = torch.tensor(arr).unsqueeze(0)

        # model switching logic
        model = light_model if MODE == "eco" else simple_model

        with torch.no_grad():
            out = model(x)
            pred = torch.argmax(out, dim = 1).item()

        return {"FoG": bool(pred), "prediction": pred, "mode": MODE}
    
    except Exception as e:
        return {"error": str(e)}

    finally:
        emissions = tracker.stop()
        print(f"inference emissions: {emissions:.4f} kg CO2")
    
    # except Exception as e:
    #     return {"error": str(e)}

        

    # x = np.array(payload["features"], dtype=np.float32).reshape(1, 128, 6)
    # x = torch.tensor(x, dtype=torch.float32)

    # with torch.no_grad():
    #     out = model(x)
    #     pred = torch.argmax(out, dim=1).item()
    # return {"FoG": bool(pred), "prediction": int(pred)}

# inference_mode = Gauge("inference_mode", "0=eco, 1=performance")

@app.post("/mode")
def set_mode(body: dict):
    global MODE

    mode = body.get("mode")

    if mode not in ["eco", "performance"]:
        return {"error": "mode must be eco or performance"}
    
    MODE = mode
    inference_mode.set(0 if mode == "eco" else 1)

    return {"mode", MODE}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")