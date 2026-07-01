# EventWatch AI - Intelligent Observability & Event Watchdog

[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688)]()
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)]()

## 🎯 Project Overview

**EventWatch AI** is a state-of-the-art, API-first intelligent observability platform. It is designed to ingest, analyze, and alert on application logs using multi-layered detection strategies, including statistical analysis and Machine Learning.

The system provides a comprehensive backend powered by **FastAPI** and a real-time monitoring dashboard built with **Streamlit**, offering a complete solution for modern DevOps and SRE teams.

---

## 🏗️ Architecture

EventWatch AI follows a modular, service-oriented architecture:

-   **Streamlit Dashboard**: Responsive frontend for visualization and analysis.
-   **FastAPI Backend**: High-performance REST API handling logic and orchestration.
-   **Service Layer**: Decoupled business logic for logs, anomalies, and alerts.
-   **Detection Engine**:
    -   **Statistical**: Rate and frequency analysis.
    -   **ML-powered**: Isolation Forest for multi-dimensional anomaly detection.
-   **Database**: PostgreSQL for persistent, relational data storage.

### Data Flow
1. Logs are ingested via REST API or File Upload.
2. `LogService` parses and persists the data.
3. `AnomalyService` runs parallel detection algorithms.
4. `AlertService` evaluates thresholds and triggers notifications.
5. `Dashboard` consumes APIs to provide real-time insights.

---

## ✨ Features

-   **🔄 Versatile Log Ingestion**: Support for single JSON entries and bulk file uploads (.log, .txt, .csv).
-   **🚨 Intelligent Alerting**: 
    -   **Error Spike Detection**: Threshold-based moving average analysis.
    -   **Pattern Recognition**: Identification of recurring incident signatures.
    -   **AI Anomalies**: ML-driven detection of unusual system behavior.
-   **📊 360° Dashboard**:
    -   **Overview**: Health scores, key metrics, and trend charts.
    -   **Log Explorer**: Advanced search, filtering, and deep-dive capabilities.
    -   **Anomaly Analysis**: Visual breakdown of ML detection results.
    -   **Alert Center**: Incident management and resolution tracking.
-   **🔌 Webhook Notifications**: Real-time integration with external systems for critical events.
-   **🛡️ Production-Ready**: Comprehensive test suite, Docker support, and robust error handling.

---

## 💻 Technology Stack

-   **Backend**: FastAPI, SQLAlchemy (v2.0), Pydantic (v2.0)
-   **Dashboard**: Streamlit, Plotly, Pandas
-   **Database**: PostgreSQL
-   **Machine Learning**: Scikit-learn (Isolation Forest)
-   **Testing**: Pytest, Pytest-Cov
-   **DevOps**: Docker, Docker Compose

---

## 🚀 Installation & Setup

### Prerequisites
-   Python 3.8+
-   PostgreSQL (or Docker)

### 1. Environment Configuration
Copy the example environment file and update your credentials:
```bash
cp config/.env.example .env
```

### 2. Manual Installation
```bash
# Clone repository
git clone https://github.com/mbilal117/eventwatch-ai.git
cd eventwatch-ai

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application

**Start the Backend:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Start the Dashboard:**
```bash
streamlit run dashboard/app.py
```

---

## 🐳 Docker Deployment

Deploy the entire stack with a single command:
```bash
docker-compose -f docker/docker-compose.yml up -d
```
-   **API**: `http://localhost:8001`
-   **Dashboard**: `http://localhost:8501`
-   **PostgreSQL**: `localhost:5432`

---

## 📖 API Documentation

The API comes with interactive Swagger documentation:
-   **Swagger UI**: `http://localhost:8001/docs`
-   **ReDoc**: `http://localhost:8001/redoc`

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/logs/ingest` | POST | Ingest a single log entry |
| `/api/logs/upload` | POST | Bulk upload log files |
| `/api/anomalies/` | GET | List detected anomalies |
| `/api/alerts/` | GET | List active alerts |
| `/api/health/score` | GET | Current system health metrics |

---

## 🧪 Testing

The project maintains high standards with a comprehensive test suite.

**Run tests:**
```bash
PYTHONPATH=. pytest tests/
```

**Run tests with coverage:**
```bash
PYTHONPATH=. pytest --cov=app tests/
```

---

## 📁 Project Structure

```text
eventwatch-ai/
├── app/                    # FastAPI Backend
│   ├── database/           # Connection and Models
│   ├── routes/             # API Controllers (Logs, Anomalies, Alerts, Health)
│   ├── schemas/            # Pydantic Validation Models
│   ├── services/           # Core Business Logic & ML Integration
│   ├── main.py             # FastAPI Entry Point
│   └── dependencies.py     # API Dependencies
├── dashboard/              # Streamlit Frontend
│   ├── components/         # API Client, Charts, and Metrics
│   ├── pages/              # Multi-page Views (Overview, Explorer, ML Analysis)
│   └── app.py              # Dashboard Entry Point
├── docker/                 # Deployment Assets
│   ├── Dockerfile.api      # Backend Container Configuration
│   ├── Dockerfile.dashboard # Dashboard Container Configuration
│   └── docker-compose.yml  # Production Orchestration
├── architecture/           # System Design Documentation
├── tests/                  # Pytest Suite (API & Service layers)
├── docs/                   # Audit and Cleanup Reports
├── submission/             # Handover Checklists
└── requirements.txt        # Project Dependencies
```

---

## 🔮 Future Enhancements
-   [ ] Prometheus/Grafana integration.
-   [ ] Advanced Natural Language Processing for log parsing.
-   [ ] Multi-tenant support and RBAC.
-   [ ] Real-time WebSocket streaming for logs.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
