# Testing Workflow – FoG Prediction Platform

This document describes the complete testing workflow for the **FoG Prediction Platform**.  
The workflow validates correct deployment, service health, end-to-end ML inference, manual and automatic control behavior, and carbon-aware sustainability mechanisms.

---

## 1. Clean System Setup

To ensure a reproducible environment, remove all existing Docker artifacts.

docker system prune  
docker volume prune  
docker compose down -v  

Rebuild and start the platform:

docker compose build  
docker compose up  

Verify that all services are running:

docker compose ps  

All containers should be in the `Up` state.

---

## 2. Service Health Checks

### 2.1 Ingestion Service

curl http://localhost:8081/health  

Expected output:

{"ok":true,"buffer_size":0,"required":128,"last_prediction":null}

---

### 2.2 Feature Service

curl http://localhost:8082/health  

Expected output:

{"ok":true,"service":"feature-extractor"}

---

### 2.3 Anomaly Service

curl http://localhost:8080/health  

Expected output:

{"ok":true,"mode":"performance","models_loaded":true}

---

### 2.4 Generator Service (Initial State)

curl http://localhost:8083/status  

Expected output:

{"running":false,"rate":"low","samples_per_second":1}

---

### 2.5 Carbon Controller (Initial State)

curl http://localhost:8084/status  

Expected output:

{"running":false,"last_rate":null,"poll_interval_rate":5}

This confirms that the Carbon Controller is inactive and operates using a polling-based control loop.

---

## 3. Start Runtime Services

### 3.1 Start Data Generator

curl -X POST http://localhost:8083/start  

Expected output:

{"running":true,"rate":"low"}

Verify:

curl http://localhost:8083/status  

---

### 3.2 Start Carbon Controller

curl -X POST http://localhost:8084/start  

Expected output:

{"running":true}

The Carbon Controller now periodically polls system state and enforces sustainability rules.

---

## 4. End-to-End Pipeline Verification

(Optional – log streaming may still be under development)

docker compose logs -f ingestion  

Verify ingestion health:

curl http://localhost:8081/health  

Example output:

{"ok":true,"buffer_size":78,"required":128,"last_prediction":null}

An increasing buffer size confirms continuous data ingestion and end-to-end ML inference.

---

## 5. Manual Model Switching Test

### 5.1 Force Eco Mode

curl -X POST http://localhost:8080/mode  
-H "Content-Type: application/json"  
-d '{"mode":"eco"}'  

Verify model mode via anomaly service:

curl http://localhost:8080/health  

Expected output:

{"ok":true,"mode":"eco","models_loaded":true}

---

### 5.2 Switch Back to Performance Mode

curl -X POST http://localhost:8080/mode  
-H "Content-Type: application/json"  
-d '{"mode":"performance"}'  

Verify again:

curl http://localhost:8080/health  

Expected output:

{"ok":true,"mode":"performance","models_loaded":true}

This confirms correct manual model switching logic.

---

## 6. Automatic Carbon-Aware Switching Test

### 6.1 Increase Generator Rate

curl -X POST http://localhost:8083/self-rate  
-H "Content-Type: application/json"  
-d '{"rate":"high"}'  

Observed behavior:

- Rate is initially set to high  
- After a few seconds it drops to medium  
- Finally it returns to low  

Explanation:  
The Carbon Controller periodically polls system metrics and overrides manual rate changes when high sampling is not clinically justified. This demonstrates autonomous, sustainability-driven control.

---

### 6.2 Observe Carbon Controller Decisions

docker compose logs -f carbon  

Expected behavior:

- Rate changes logged by the controller  
- Automatic correction to energy-efficient settings  

---

## 7. Manual Performance Mode Override Test

### 7.1 Force Performance Mode

curl -X POST http://localhost:8080/mode  
-H "Content-Type: application/json"  
-d '{"mode":"performance"}'  

Observed behavior:

- If the rate is high, performance mode immediately switches back to eco  
- If the rate is medium, performance mode is allowed briefly, then switches back to eco  
- If the rate is low, performance mode switches back to eco  

Explanation:  
High-cost inference is only allowed when system conditions justify it. The Carbon Controller enforces eco mode by default to minimize energy usage.

---

## 8. Dynamic Sustainability Scenario

### 8.1 Monitor Ingestion Buffer

while true; do  
  curl -s http://localhost:8081/health  
  echo  
  sleep 1  
done  

---

### 8.2 Monitor Generator Status

while true; do  
  curl -s http://localhost:8083/status  
  echo  
  sleep 1  
done  

---

### 8.3 Monitor Anomaly Service

while true; do  
  curl -s http://localhost:8080/health  
  echo  
  sleep 1  
done  

---

### 8.4 Force High Rate Again

curl -X POST http://localhost:8083/self-rate  
-H "Content-Type: application/json"  
-d '{"rate":"high"}'  

Observed behavior:

- Temporary increase in rate  
- Automatic reduction by Carbon Controller  
- Eco mode enforced for sustainability  

---

## 9. Observability Verification

### 9.1 Prometheus

Open in browser:

http://localhost:9090  

Verify metrics such as generator rate, buffer pressure, and inference mode.

---

### 9.2 Grafana

Open in browser:

http://localhost:3000  

Default credentials:  
Username: admin  
Password: admin  

Verify dashboards and metric visualization.

---

## 10. Shutdown

docker compose down  

---

## 11. Workflow Summary

This workflow verifies:

- Correct microservice deployment  
- End-to-end FoG prediction pipeline  
- Manual and automatic inference mode switching  
- Polling-based carbon-aware control  
- Observable, sustainability-driven system behavior  

The FoG Prediction Platform demonstrates an adaptive AI architecture that balances accuracy, performance, and environmental impact.

