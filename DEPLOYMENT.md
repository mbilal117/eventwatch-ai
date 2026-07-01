# EventWatch AI Deployment Guide

This guide provides instructions for deploying EventWatch AI in various environments.

## 🐳 Docker Deployment (Recommended)

The easiest way to run the entire EventWatch AI stack is using Docker Compose.

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Configure Environment Variables**
   Create a `.env` file in the root directory (optional if using defaults in docker-compose).

2. **Launch the Stack**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. **Verify Deployment**
   - **Backend API**: http://localhost:8001/api/health/score
   - **Dashboard**: http://localhost:8501
   - **API Docs**: http://localhost:8001/docs

### ⚙️ Services
- **eventwatch-db**: PostgreSQL 15 database.
- **eventwatch-api**: FastAPI backend application.
- **eventwatch-dashboard**: Streamlit frontend.

---

## 🛠️ Manual Deployment

### 1. Database Setup
Ensure you have a PostgreSQL instance running.
```bash
# Create database
createdb eventwatch
```

### 2. Backend Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+psycopg2://user:password@localhost/eventwatch

# Run API
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 3. Dashboard Setup
```bash
source venv/bin/activate
export BACKEND_URL=http://localhost:8001
streamlit run dashboard/app.py --server.port 8501
```

---

## 🛡️ Production Hardening
- **Reverse Proxy**: Use Nginx or Traefik as a reverse proxy for the Dashboard and API.
- **SSL**: Enable TLS using Let's Encrypt.
- **Database Backups**: Schedule regular dumps of the `postgres_data` volume.
- **Monitoring**: Integrate with Prometheus/Grafana (future enhancement).
