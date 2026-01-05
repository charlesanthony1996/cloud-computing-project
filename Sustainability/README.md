# Sustainability Report  
## FoG Prediction Platform

---

## 1. Introduction

The **FoG Prediction Platform** was designed with sustainability as a core architectural concern, alongside accuracy, modularity, and observability.  
The system processes continuous gait sensor data to detect *Freezing of Gait (FoG)* events using machine learning, while dynamically adapting its behavior to reduce energy consumption and carbon emissions.

Sustainability is addressed both at **design time** (architecture and deployment decisions) and at **runtime** (carbon-aware control and monitoring).

---

## 2. Sustainability Considerations in Deployment

The platform explicitly considers trade-offs between **scalability, energy efficiency, and cost**.  
Rather than optimizing for maximum scalability, the system prioritizes **efficient resource usage and adaptive behavior**, which is more appropriate for continuous monitoring workloads with variable demand.

A **container-based deployment** using Docker Compose on a single host was chosen to minimize baseline energy consumption while maintaining modularity and reproducibility.

---

## 3. Deployment Strategy (Sustainability Focus)

### 3.1 Containers vs. Alternative Cloud Approaches

The platform uses **Docker containers**, with one container per microservice, instead of serverless or large-scale orchestration platforms.

This choice was made because:
- Containers provide **predictable and measurable resource usage**
- A single-host deployment minimizes idle infrastructure
- Energy overhead from autoscaling platforms is avoided
- Individual services can be controlled independently

While deployed locally, the architecture remains **portable to cloud environments** due to its container-based design.

---

## 4. Carbon Footprint Assessment

### 4.1 Explicit Carbon Measurement

The **Anomaly Service** uses the **CodeCarbon** Python library to measure carbon emissions during machine learning inference.

Key characteristics:
- Emissions are measured per inference execution
- Results are reported in **kg CO₂ equivalent**
- Measurements are tied to actual computation, not estimates

This fulfills the requirement for **explicit carbon footprint assessment**.

---

### 4.2 Sustainability Metrics and Observability

System and sustainability-related metrics are exposed via **Prometheus** and visualized using **Grafana**.  
These metrics include inference mode, data generation rate, buffer pressure, and prediction activity.

This ensures sustainability is:
- Observable at runtime
- Measurable and auditable
- Treated as an operational concern

---

## 5. Carbon-Aware Runtime Behavior

### 5.1 Carbon Controller

A dedicated **Carbon Controller service** implements a feedback control loop that adapts system behavior at runtime.

Instead of relying on an external carbon-intensity API, the system **simulates carbon-aware behavior** using internal system signals such as:
- Ingestion buffer pressure
- System activity level
- Detection of FoG events

---

### 5.2 Adaptive Data Generation

The Generator Service supports multiple sampling rates:
- **Low** – energy-efficient baseline
- **Medium** – balanced operation
- **High** – increased resolution during critical events

The Carbon Controller dynamically adjusts the rate to reduce unnecessary computation while preserving diagnostic accuracy.

---

### 5.3 Energy-Aware Model Selection

The Anomaly Service supports two inference modes:
- **Eco mode** – lightweight LSTM model with reduced computational cost
- **Performance mode** – larger LSTM model with higher accuracy

The system defaults to eco mode and switches to performance mode only when clinically relevant FoG events are detected.

---

## 6. Sustainability Trade-Off Analysis

### 6.1 Accuracy vs Energy Consumption

| Mode | Accuracy | Energy Usage |
|------|----------|--------------|
| Eco Mode | Moderate | Low |
| Performance Mode | High | Higher |

The platform prioritizes energy efficiency by default, increasing computational cost only when justified.

---

### 6.2 Scalability vs Cost

- Single-host deployment limits horizontal scalability
- Reduced infrastructure complexity lowers energy and cost overhead
- Microservice design preserves future scalability options

This trade-off is intentional and aligned with sustainability goals.

---

### 6.3 Latency vs Sustainability

- Lower sampling rates reduce energy usage but increase latency
- Higher rates improve responsiveness at increased carbon cost

The Carbon Controller dynamically balances this trade-off.

---

## 7. Alignment with Course Requirements

The FoG Prediction Platform satisfies all sustainability-related project requirements:

- Sustainability considerations in deployment
- Justified deployment strategy
- Explicit carbon footprint measurement using CodeCarbon
- Carbon-aware runtime behavior
- Clear discussion of efficiency, carbon footprint, and cost trade-offs

---

## 8. Conclusion

Sustainability in the FoG Prediction Platform is implemented as a **measurable, adaptive, and enforceable system property**.  
Through container-based deployment, explicit carbon measurement, adaptive inference, and carbon-aware control logic, the system demonstrates how AI-driven architectures can balance performance, cost, and environmental impact.

