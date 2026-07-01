# EventWatch AI Prompt Audit Log

## Prompt 001

Project selected:
Intelligent Observability & Event Watchdog

Lead Architect mode: ON. We are building a Python-based, API-first EventWatch AI using a free database and a dashboard.

Rules:

No Manual Edits: You provide all logic and fixes. I will not edit any code.
Audit Log: You must maintain a file named prompts.md.
Time-Check: Start a timer. Goal is an MVP in 4-6 hours.

Acknowledge and let's start.

## Prompt 002

1. What types of events should we watch? (logs, metrics, traces, etc.)
   - Primary focus: Logs.
   - Sources:
     - Application logs
     - Platform logs
     - API service logs
   - Future enhancement:
     - Metrics
     - Traces
   - For MVP, implement log-based observability only.

2. What are key alert conditions? (thresholds, patterns, anomalies)
   - Answer: Implement the following alert conditions:
     1. Error Spike Detection
        - Error count exceeds moving average by configurable threshold.
     2. Repeated Error Pattern
        - Same error message occurs repeatedly within a time window.
     3. Sudden Increase in Error Rate
        - Error volume increases significantly compared to previous period.
     4. AI-Based Anomaly Detection
        - Use Isolation Forest to identify abnormal behavior patterns.
   - Severity Levels:
     - Low
     - Medium
     - High
     - Critical
   - Generate webhook alerts for High and Critical events.

3. Any specific dashboards you need? (real-time streams, trends, SLA tracking)
   - Answer: Dashboard Requirements:
     1. System Health Score
     2. Total Logs Processed
     3. Error Count
     4. Warning Count
     5. Anomaly Count
     6. Recent Alerts
   - Visualizations:
     - Error Trend Over Time
     - Error Distribution by Severity
     - Alert History Timeline
   - Dashboard Style:
     - Trend-focused operational dashboard
     - Historical trend analysis
     - Health monitoring
   - Real-time streaming is optional and not required for MVP.
   - SLA tracking can be considered a future enhancement.

## Prompt 003

Review the proposed architecture.
Requirements:
1. Replace SQLite with PostgreSQL.
2. Avoid a monolithic main.py file.
3. Separate routes, services, models, schemas and database configuration.
4. Keep the architecture simple enough for a 4-6 hour MVP.
5. Recommend Streamlit for the dashboard if it reduces complexity.
6. Generate an updated folder structure only and removed unused folders
7. Do not generate code.

## Prompt 004

Generate the complete final project directory structure as a tree view.
Show every folder and file that will exist for the MVP.
Do not generate code.
Include:
- FastAPI backend
- PostgreSQL
- SQLAlchemy
- Streamlit dashboard
- Anomaly detection
- Webhook alerting
- Docker
- Tests
- Documentation

## Prompt 005

Based on the approved architecture, generate the complete MVP file tree with actual file names.
Requirements:
- Optimized for a 4–6 hour challenge.
- Avoid unnecessary complexity.
- Keep strong separation of concerns.
- Include only files required for the MVP.
- Show the final tree structure only.
- Do not generate code.

## Prompt 006

Lead Architect mode: ON.
Generate the complete backend implementation for EventWatch AI.
Project:
AI-Powered Intelligent Observability & Event Watchdog
Technology Stack:
- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- scikit-learn
- Docker
Architecture:
- routes/
- services/
- database/
- schemas/
- config/
Requirements:
1. Log Ingestion
   - Upload .log, .txt and .csv files
   - Parse log entries
   - Store logs in PostgreSQL
2. Anomaly Detection
   - Statistical threshold detection
   - Error spike detection
   - Repeated error pattern detection
   - Isolation Forest anomaly detection
3. Alerting
   - Generate alerts
   - Severity levels:
     - Low
     - Medium
     - High
     - Critical
   - Simulate webhook notifications
4. API Endpoints
   - POST /api/logs/upload
   - GET /api/logs
   - GET /api/anomalies
   - GET /api/alerts
   - GET /api/health
5. Database
   - Create models for:
     - logs
     - anomalies
     - alerts
     - alert_history
     - system_health
6. Best Practices
   - Type hints
   - Dependency injection
   - Structured logging
   - Exception handling
   - Environment variables
   - Clean architecture
   - SOLID principles
Generate:
- Complete file tree
- All backend source code
- requirements.txt
- .env.example
Do not generate dashboard code.
Do not generate tests.
Do not generate documentation

## Prompt 007

Generate the complete Streamlit dashboard.

Pages:
- Overview Dashboard
- Log Explorer
- Anomaly Analysis
- Alert Center

Widgets:
- Health Score
- Total Logs
- Error Count
- Warning Count
- Anomaly Count
- Active Alerts

Charts:
- Error Trends
- Severity Distribution
- Alert Timeline

Dashboard must consume FastAPI APIs.

## Prompt 008

Perform dashboard integration testing.

Tasks:
- Verify API connectivity
- Align dashboard schema with backend responses
- Fix alert timeline visualization
- Fix anomaly score visualizations
- Fix alert center rendering
- Validate all dashboard pages

## Prompt 009

Validate the complete EventWatch AI solution.

Checklist:
- FastAPI starts successfully
- PostgreSQL connected
- Health endpoint healthy
- Log upload working
- Anomaly detection working
- Alert generation working
- Dashboard operational
- GitHub repository updated

Outcome:
Production-ready MVP successfully deployed and validated.
