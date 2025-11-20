from fastapi import FastAPI, Body
import torch, os, numpy as np
from model_lstm import SimpleLstm, train_lstm

app = FastAPI(title="Anomaly service - lstm trainer & inference")

model_path = "lstm_model.pt"
# train_folder = "/app/train/defog/train"
train_folder = "/app/train"

# train if missing
if not os.path.exists(model_path):
    print("training model since lstm_model.pt not found")
    model = train_lstm(train_folder)

else:
    model = SimpleLstm()
    model.load_state_dict(torch.load(model_path, map_location= torch.device("cpu")))
    print("loaded existing model from lstm_model.pt")

model.eval()

@app.get("/health")
def health():
    return { "ok": True, "model": "SimpleLSTM", "trained": os.path.exists(model_path)}

@app.post("/predict")
def predict(payload: dict = Body(...)):
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

        with torch.no_grad():
            out = model(x)
            pred = torch.argmax(out, dim = 1).item()

        return {"FoG": bool(pred), "prediction": pred}
    
    except Exception as e:
        return {"error": str(e)}

        

    # x = np.array(payload["features"], dtype=np.float32).reshape(1, 128, 6)
    # x = torch.tensor(x, dtype=torch.float32)

    # with torch.no_grad():
    #     out = model(x)
    #     pred = torch.argmax(out, dim=1).item()
    # return {"FoG": bool(pred), "prediction": int(pred)}