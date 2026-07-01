# EventWatch AI Architecture

This document describes the high-level architecture of the EventWatch AI system.

## 🏗️ System Overview

EventWatch AI is a modular observability platform designed for intelligent log analysis and anomaly detection. It follows a decoupled, service-oriented architecture.

```mermaid
graph TD
    subgraph Frontend
        SD[Streamlit Dashboard]
    end

    subgraph Backend
        FA[FastAPI Gateway]
        LS[Log Service]
        AS[Anomaly Service]
        AL[Alert Service]
        WS[Webhook Service]
    end

    subgraph Storage
        DB[(PostgreSQL)]
    end

    subgraph External
        WHE[Webhook Endpoints]
    end

    SD -- REST API --> FA
    FA --> LS
    FA --> AS
    FA --> AL
    
    LS --> DB
    AS --> DB
    AL --> DB
    
    AS -. Triggers .-> AL
    AL --> WS
    WS -- HTTP POST --> WHE
```

---

## 🛰️ Layered Architecture

### 1. Dashboard Layer (Streamlit)
The user interface is built with Streamlit, providing a real-time view of system health, log trends, and detected anomalies.
- **Overview**: High-level metrics and health scores.
- **Log Explorer**: Deep search and filtering.
- **Anomaly Analysis**: Visualization of ML detection results.
- **Alert Center**: Incident management.

### 2. API Layer (FastAPI)
Acts as the entry point for all internal and external communication.
- **Pydantic Validation**: Ensures data integrity.
- **Async Operations**: High-performance log ingestion.
- **Interactive Documentation**: Swagger/OpenAPI support.

### 3. Service Layer
Contains the core business logic, decoupled from the API endpoints.
- **LogService**: Handles ingestion, bulk uploads, and retrieval.
- **AnomalyService**: Orchestrates detection runs using statistical and ML models.
- **AlertService**: Evaluates rules and triggers notifications.
- **WebhookService**: Integrates with external systems.

### 4. Data Layer (PostgreSQL)
Persistent storage for all platform data.
- **Logs**: Historical event data.
- **Anomalies**: Detected deviations.
- **Alerts**: Incident records.

---

## 📈 Data Flow

### Log Ingestion & Detection Flow
1. **Ingest**: Logs arrive via API or File Upload.
2. **Process**: `LogService` parses and saves to DB.
3. **Analyze**: `AnomalyService` runs detection algorithms:
    - Statistical Analysis (Rate/Spikes)
    - Machine Learning (Isolation Forest)
4. **Alert**: If an anomaly is confirmed or thresholds met, `AlertService` creates an alert.
5. **Notify**: `WebhookService` sends payload to external endpoints.

```mermaid
sequenceDiagram
    participant App as External Source
    participant API as FastAPI
    participant LS as Log Service
    participant AS as Anomaly Service
    participant AL as Alert Service
    participant DB as Database

    App->>API: POST /api/logs/ingest
    API->>LS: save_log(data)
    LS->>DB: INSERT INTO logs
    API->>AS: trigger_detection(log_id)
    AS->>DB: SELECT recent logs
    AS-->>AS: Run ML Inference
    AS->>AL: create_alert_if_needed()
    AL->>DB: INSERT INTO alerts
    API-->>App: 201 Created
```

---

## 🚀 Deployment Architecture

The system is containerized using Docker, allowing for easy scaling of the Dashboard and API components.

```mermaid
graph LR
    User((User)) --> LB[Load Balancer]
    subgraph Docker Network
        LB --> SD[Streamlit Container]
        LB --> FA[FastAPI Container]
        FA --> PG[(PostgreSQL Container)]
    end
```
