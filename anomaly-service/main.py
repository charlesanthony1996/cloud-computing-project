from fastapi import FastAPI, Body, Response
import torch
import os
import numpy as np
from model_lstm import SimpleLstm, train_lstm, LightLstm
from codecarbon import EmissionsTracker

from prometheus_client import Gauge, generate_latest, Counter

import random
import time
from codecarbon import EmissionsTracker

# Simulated carbon intensity (kg CO2e / kWh) - in real world fetched from electricity maps API
# For demo: pretend it changes over time or based on time of day
def get_simulated_carbon_intensity():
    # Example: higher during peak hours (simulated)
    hour = time.localtime().tm_hour
    if 8 <= hour <= 20:  # day = higher carbon (coal/gas mix)
        return 0.55
    else:
        return 0.25  # night = lower (more renewables)
    
# Config via env (for future k8s configMap / secret)
CARBON_THRESHOLD = float(os.getenv("CARBON_THRESHOLD", "0.40"))  # kg CO2e/kWh
SLO_LATENCY_MS = 500  # example SLO: p95 latency < 500ms
SLO_ERROR_RATE = 0.01

# Global flag for which model to use (eco = light, performance = simple)
USE_LIGHT_MODEL = True  # default eco


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


# NEW CARBON METRICS
carbon_emissions_total = Counter("carbon_emissions_kg_total", "Total CO2 emissions in kg")
carbon_emissions_per_request = Gauge("carbon_emissions_last_request_kg", "Last request CO2 emissions in kg")
carbon_emissions_rate = Gauge("carbon_emissions_rate_g_per_sec", "CO2 emissions rate in g/sec")

# Track emissions over time for rate calculation
emission_history = []
emission_window_size = 100  # Keep last 100 requests

# NEW ENERGY METRICS
energy_consumed_total = Counter("energy_consumed_kwh_total", "Total energy consumed in kWh")
energy_per_request = Gauge("energy_last_request_wh", "Last request energy in Wh")
power_consumption = Gauge("power_consumption_watts", "Current power consumption in Watts")
inference_duration = Gauge("inference_duration_ms", "Last inference duration in ms")

# Energy efficiency metric (predictions per kWh)
predictions_per_kwh = Gauge("predictions_per_kwh", "Energy efficiency: predictions per kWh")

# Track metrics for efficiency calculation
total_predictions = 0
total_energy_kwh = 0.0


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

# @app.post("/predict")
# def predict(payload: dict = Body(...)):

#     tracker = EmissionsTracker(
#         project_name="fog-inference",
#         measure_power_specs=1,
#         log_level="error"
#     )

#     tracker.start()

#     try:
#         arr = np.array(payload["features"], dtype=np.float32)

#         # validate: must be (n, 3)
#         if arr.ndim != 2 or arr.shape[1] != 3:
#             return {"error": "features must be list of [AccV, AccML, AccAP] triplets"}
        
#         # zero pad or truncate to exactly 128 steps
#         if arr.shape[0] >= 128:
#             arr = arr[:128]

#         else:
#             padding = np.zeros((128 - arr.shape[0], 3), dtype=np.float32)
#             arr = np.vstack((arr, padding))

#         x = torch.tensor(arr).unsqueeze(0)

#         # model switching logic
#         model = light_model if MODE == "eco" else simple_model

#         with torch.no_grad():
#             out = model(x)
#             pred = torch.argmax(out, dim = 1).item()

#         return {"FoG": bool(pred), "prediction": pred, "mode": MODE}
    
#     except Exception as e:
#         return {"error": str(e)}

#     finally:
#         emissions = tracker.stop()
#         print(f"inference emissions: {emissions:.4f} kg CO2")
    
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



@app.post("/predict")
def predict(payload: dict):
    global USE_LIGHT_MODEL

    start_time = time.time()

    tracker = EmissionsTracker()
    tracker.start()

    try:
        # Simulate carbon-aware decision (every request or every few minutes)
        current_intensity = get_simulated_carbon_intensity()

        if current_intensity > CARBON_THRESHOLD:
            # High carbon → force eco mode (light model)
            USE_LIGHT_MODEL = True
            print(f"[Carbon Aware] High intensity ({current_intensity:.2f}) → eco mode")
        else:
            # Low carbon → allow performance mode if SLOs ok
            # In real: check Prometheus metrics (latency, error rate)
            # Here we simulate: assume SLO ok 90% of time
            if random.random() < 0.9:
                USE_LIGHT_MODEL = False
                print(f"[Carbon Aware] Low intensity → performance mode (SLO ok)")
            else:
                USE_LIGHT_MODEL = True
                print(f"[Carbon Aware] Low intensity but SLO violation → fallback eco")

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

        # Measure emissions for this request
        emissions_kg = tracker.stop()

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        inference_duration.set(duration_ms)

        # Get energy data from CodeCarbon
        # CodeCarbon tracks energy internally - we estimate based on duration and typical power
        # For more accurate tracking, you'd parse CodeCarbon's output
        
        # Typical power consumption estimates (adjust based on your hardware)
        # CPU inference: 15-30W for simple model, 5-10W for light model
        estimated_power_watts = 25.0 if MODE == "performance" else 8.0


        # Energy = Power × Time
        energy_kwh = (estimated_power_watts * (duration_ms / 1000) / 3600) / 1000
        energy_wh = energy_kwh * 1000  # Convert to Wh for readability


        # Update Prometheus metrics
        if emissions_kg and emissions_kg > 0:
            carbon_emissions_total.inc(emissions_kg)
            carbon_emissions_per_request.set(emissions_kg)
        
        if energy_kwh > 0:
            energy_consumed_total.inc(energy_kwh)
            energy_per_request.set(energy_wh)
            power_consumption.set(estimated_power_watts)

            # Update efficiency metric
            total_predictions += 1
            total_energy_kwh += energy_kwh
            
            if total_energy_kwh > 0:
                efficiency = total_predictions / total_energy_kwh
                predictions_per_kwh.set(efficiency)

            print(f"[Energy] Power: {estimated_power_watts:.1f}W | "
                  f"Energy: {energy_wh:.4f}Wh | "
                  f"Duration: {duration_ms:.1f}ms | "
                  f"Mode: {MODE}")
            
            # Track emission history for rate calculation
            emission_history.append(emissions_kg)
            if len(emission_history) > emission_window_size:
                emission_history.pop(0)
            
            # Calculate emissions rate (g/sec)
            # Assuming ~1 request takes ~0.1 seconds
            avg_emissions = sum(emission_history) / len(emission_history)
            emissions_rate_g = (avg_emissions * 1000) / 0.1  # Convert to g/sec
            carbon_emissions_rate.set(emissions_rate_g)
            
            print(f"[Carbon] Inference emissions: {emissions_kg:.6f} kg CO2 (mode: {MODE})")
        print(f"Request emissions: {emissions_kg:.6f} kg CO2e")

        return {
            "FoG": bool(pred), 
            "mode": "eco" if USE_LIGHT_MODEL else "performance", 
            "emissions_kg": emissions_kg, 
            "energy_wh": energy_wh,
            "power_watts": estimated_power_watts,
            "duration_ms": duration_ms
        }

    except Exception as e:
        tracker.stop()
        return {"error": str(e)}