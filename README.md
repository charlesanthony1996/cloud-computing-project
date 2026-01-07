# FoG Prediction Platform  
**Freezing of Gait (FoG) Prediction – Carbon-Aware Microservice Architecture**

---

## Overview

The **FoG Prediction Platform** is a microservice-based system designed to detect *Freezing of Gait (FoG)* events from continuous gait sensor data using machine learning.  
In addition to diagnostic accuracy, the platform places strong emphasis on **sustainability**, **observability**, and **adaptive runtime behavior**.

The system is implemented using **Docker Compose**, exposes REST APIs for all services, and includes a **carbon-aware control layer** that dynamically adapts system behavior to reduce unnecessary energy consumption.

---

## Key Features

- Microservice-based FoG detection pipeline
- Continuous gait data generation and ingestion
- Feature extraction and ML-based anomaly detection
- Explicit carbon footprint measurement using CodeCarbon
- Polling-based carbon-aware control logic
- Adaptive data generation rate and inference mode switching
- Observability using Prometheus and Grafana
- Reproducible deployment using Docker Compose

---

## System Architecture

The platform consists of the following subsystems:

- **Generator Service** – produces gait sensor data
- **Ingestion Service** – buffers incoming data
- **Feature Service** – extracts gait features
- **Anomaly Service** – performs FoG prediction
- **Carbon Controller Service** – enforces sustainability rules
- **Prometheus** – collects metrics
- **Grafana** – visualizes metrics

Detailed architecture documentation is available in the `UML-Diagram/` directory:
- Use Case Diagram
- Component Diagram
- Sequence Diagram
- Deployment Diagram

---

## Architecture Decision Records (ADR)

Key architectural decisions are documented in:

```
docs/adr/
```

---

## Explicit Runtime Activation (Important)

> **Containers do not imply active behavior.**

Two services are intentionally designed to require **explicit runtime activation**:

- **Generator Service**
- **Carbon Controller Service**

They do **not start automatically** when containers are launched.

### Why this matters

- Prevents unnecessary computation when the system is idle
- Avoids continuous polling and data generation
- Reinforces sustainability as a **runtime-enforced property**
- Ensures energy-efficient operation by default

This behavior is intentional and aligns with the platform’s sustainability goals.

---

## Runtime Behavior

The FoG Prediction Platform operates as a continuously running microservice pipeline.  
Once deployed, **services start in an idle state** and require **explicit runtime activation**.

At runtime:
- The **Generator Service** must be explicitly started to begin streaming gait sensor data.
- The **Carbon Controller** must be explicitly started to activate sustainability control logic.
- Data flows through the pipeline: Generator → Ingestion → Feature → Anomaly.
- Inference runs continuously while data is available.
- System metrics are exposed and collected via Prometheus and visualized using Grafana.

The platform does not automatically generate data or enforce carbon-aware control unless these services are explicitly activated.

---

## Carbon-Aware Control Design

The platform implements a **polling-based carbon-aware control mechanism** via a dedicated Carbon Controller service.

Key characteristics:
- The Carbon Controller periodically polls internal system metrics (e.g., buffer pressure, data rate, inference activity).
- Decisions are based on **internal system state**, not external carbon-intensity APIs.
- The controller dynamically adjusts:
  - Data generation rate (low / medium / high)
  - Inference mode (eco / performance)

Manual changes to generator rate or inference mode are treated as **temporary overrides** and may be reverted automatically to maintain energy-efficient operation.

The system initializes in **performance mode** to ensure diagnostic accuracy during startup, but the Carbon Controller actively switches to **eco mode** during normal operation. Data generation defaults to **low sampling rate**, escalating only when buffer pressure or FoG events require higher resolution.

---

## Offline Model Training

Machine learning model training is performed **offline** and is **not part of the runtime pipeline**.

Training characteristics:
- Models are trained using a dedicated training service or scripts.
- Two models are produced:
  - A lightweight LSTM model for eco mode
  - A larger LSTM model for performance mode
- Trained models are stored as `.pt` files and loaded at runtime by the Anomaly Service.

Separating training from inference:
- Prevents energy-intensive workloads during continuous operation
- Improves runtime sustainability
- Ensures predictable and stable inference performance

Only inference runs in production; training is executed manually when models need to be updated.

---

## Testing Workflow

A complete testing workflow is provided in:

```
Testing-workflow/testing_workflow.md
```

It validates:

- Service health checks  
- End-to-end ML inference  
- Manual model switching  
- Automatic carbon-aware control  
- Observability and monitoring  

---

## Sustainability Documentation

The sustainability report is available in:

```
Sustainability/README.md
```

It covers:

- Deployment trade-offs  
- Carbon footprint measurement  
- Runtime sustainability mechanisms  
- Accuracy vs energy trade-offs  

---

## Summary

The FoG Prediction Platform demonstrates a complete AI architecture that integrates machine learning, microservices, observability, sustainability, and runtime adaptive control.

The system performs continuous Freezing of Gait (FoG) detection using an LSTM-based inference pipeline, while dynamically adapting data generation rates and inference modes through a carbon-aware control loop to reduce energy consumption without sacrificing diagnostic accuracy.



