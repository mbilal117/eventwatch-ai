# EventWatch AI System Design

## 🧠 Detection Engine

The core of EventWatch AI is its multi-layered detection engine, which balances speed (statistical) with depth (Machine Learning).

### 1. Statistical Detection
- **Spike Detection**: Uses a 5-minute rolling window to compare current error rates against a baseline.
- **Pattern Recognition**: Identifies identical error messages occurring within a short interval.

### 2. ML Detection (Isolation Forest)
- **Model**: `sklearn.ensemble.IsolationForest`
- **Features**:
  - `timestamp_hour`: Hour of day (captures temporal patterns).
  - `level_numeric`: Severity weight.
  - `message_length`: Statistical property of the log.
- **Training**: Auto-triggers after 10 logs (initially) to build a baseline, then refines.
- **Inference**: Each log is scored. If the score is below the contamination threshold (-1 in raw terms), it is flagged as an anomaly.

## 🗄️ Database Design

We use PostgreSQL for its reliability and JSONB support (though currently using structured schemas for core performance).

### Tables

#### `logs`
| Column | Type | Description |
|---|---|---|
| `id` | UUID/Serial | Primary Key |
| `timestamp` | DateTime | Event time |
| `source` | Enum | app/api/system/platform |
| `level` | Enum | INFO/WARN/ERROR/CRITICAL |
| `message` | Text | Main log content |
| `service` | String | Originating service name |
| `metadata` | JSONB | Structured extra data |

#### `anomalies`
| Column | Type | Description |
|---|---|---|
| `id` | UUID/Serial | Primary Key |
| `log_id` | Foreign Key | Link to `logs.id` |
| `detection_method` | String | ML / Statistical |
| `severity` | Enum | Low/Medium/High/Critical |
| `score` | Float | Probability/Anomaly score |

#### `alerts`
| Column | Type | Description |
|---|---|---|
| `id` | UUID/Serial | Primary Key |
| `type` | String | SPIKE / ML_ANOMALY / etc |
| `severity` | Enum | Match anomaly severity |
| `status` | Enum | ACTIVE / RESOLVED |

---

## 🛡️ Security & Reliability

- **Input Sanitization**: All incoming logs are validated via Pydantic.
- **Graceful Fallback**: The ML model falls back to statistical detection if training data is insufficient.
- **Scalability**: Stateless service design allows for multiple API workers.
- **Observability**: The platform monitors its own health via the `/api/health` endpoint.
