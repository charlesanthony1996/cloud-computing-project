# Sustainability Report  
## FoG Prediction Platform

---

## 1. Introduction

The **FoG Prediction Platform** was designed with sustainability as a core architectural concern, alongside accuracy, modularity, and observability.  
The system processes continuous gait sensor data to detect *Freezing of Gait (FoG)* events using machine learning, while dynamically adapting its behavior to reduce energy consumption and carbon emissions.

Sustainability is addressed both at **design time** (architecture and deployment decisions) and at **runtime** (carbon-aware control, adaptive inference, and monitoring).

---

## 2. Sustainability Considerations in Deployment

The platform explicitly considers trade-offs between **scalability, energy efficiency, and cost**.  
Rather than optimizing for maximum scalability, the system prioritizes **efficient resource usage and adaptive behavior**, which is more appropriate for continuous monitoring workloads with variable demand.

A **container-based deployment** using Docker Compose on a single host was chosen to minimize baseline energy consumption while maintaining modularity and reproducibility.

In addition, **model training is handled separately from runtime inference**, ensuring that energy-intensive training workloads do not impact the sustainability of continuous system operation.

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
- Emissions are measured **at runtime for each inference execution**
- Results are reported in **kg CO₂ equivalent**
- Measurements are tied to actual computation, not estimates

This fulfills the requirement for **explicit carbon footprint assessment**.

---

### 4.2 Sustainability Metrics and Observability

System and sustainability-related metrics are exposed via **Prometheus** and visualized using **Grafana**.

These metrics include:
- Inference mode selection (**eco vs performance**)
- Data generation rate
- Ingestion buffer pressure
- Prediction activity and system load

This ensures sustainability is:
- Observable at runtime
- Measurable and auditable
- Treated as an operational concern rather than a conceptual one

---

## 5. Carbon-Aware Runtime Behavior

### 5.1 Carbon Controller

A dedicated **Carbon Controller service** implements a **polling-based feedback control loop** that adapts system behavior at runtime.  
The controller periodically queries internal system state every **5 seconds**, including ingestion buffer pressure and recent prediction outcomes.

**Explicit Startup Design:**  
Both the Generator Service and Carbon Controller require **manual activation via POST requests** after container deployment. This design choice ensures:
- Services remain inactive until explicitly needed
- Zero energy consumption during idle periods
- Sustainability-by-default system behavior
- Clear operational control over resource usage

The explicit startup requirement is operationalized as:

# Activate data generation
curl -X POST http://localhost:8083/start

# Activate carbon-aware control
curl -X POST http://localhost:8084/start

---

### 5.2 Adaptive Data Generation

The Generator Service supports multiple sampling rates:
- **Low (1 sample/second)** – energy-efficient baseline
- **Medium (5 samples/second)** – balanced operation
- **High (10 samples/second)** – increased resolution during critical events

---

### 5.3 Energy-Aware Model Selection

The Anomaly Service supports **two inference models**:
- **Eco mode** – Light LSTM with 8 hidden units, reduced computational cost
- **Performance mode** – Simple LSTM with 32 hidden units, higher accuracy

**Default Behavior:**
The system initializes in **performance mode** to ensure maximum diagnostic accuracy during startup and initial operation. However, the Carbon Controller actively monitors system state and switches to eco mode when conditions allow for energy savings without compromising clinical effectiveness.

This design prioritizes **initial accuracy** while enabling **runtime energy optimization** through the carbon-aware control loop. The Carbon Controller dynamically adjusts the inference mode based on:
- Detection of FoG events (escalate to performance)
- Normal operation periods (reduce to eco)
- System load and buffer pressure

Manual inference mode changes via the `/mode` endpoint are treated as **temporary overrides** and may be reverted by the Carbon Controller to maintain optimal balance between accuracy and energy efficiency.

---

## 6. Sustainability Trade-Off Analysis

### 6.1 Accuracy vs Energy Consumption

| Mode | Accuracy | Energy Usage |
|------|----------|--------------|
| Eco Mode | Moderate | Low |
| Performance Mode | High | Higher |

**Initial Mode Selection:**
The platform defaults to performance mode at startup to ensure maximum accuracy during system initialization and validation. Once the Carbon Controller activates, it takes over mode management and switches to eco mode during normal operation. This approach balances the need for reliable startup diagnostics with long-term energy efficiency, increasing computational cost only when clinically justified.

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

The Carbon Controller dynamically balances this trade-off at runtime.

---

## 7. Conclusion

Sustainability in the FoG Prediction Platform is implemented as a **measurable, adaptive, and enforceable system property**.  

Through container-based deployment, explicit carbon measurement, offline model training, adaptive inference, explicit service activation, and polling-based carbon-aware control logic, the system demonstrates how AI-driven architectures can balance performance, cost, and environmental impact.

The platform treats sustainability as a **first-class architectural concern** alongside traditional quality attributes such as reliability, performance, and security. This approach provides a template for designing future AI systems that are both effective and environmentally responsible.



