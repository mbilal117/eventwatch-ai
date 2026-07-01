# Cleanup Summary - EventWatch AI

This document outlines the files and folders identified for removal, consolidation, or retention as part of the production-readiness audit.

## Cleanup Report

### Safe to Remove

| Path | Type | Reason | Risk Level |
|------|------|--------|------------|
| `app/database.py` | File | Superseded by `app/database/connection.py` | Low |
| `app/models.py` | File | Superseded by `app/database/models.py` | Low |
| `app/schemas.py` | File | Superseded by `app/schemas/` subpackage | Low |
| `test_api.py` | File | Standalone test script, to be replaced by Pytest suite | Low |
| `run.py` | File | Redundant entry point | Low |
| `run.sh` | File | Redundant startup script | Low |
| `start.sh` | File | Redundant startup script | Low |
| `eventwatch.db` | File | Local SQLite database (should be in .gitignore) | Low |
| `prompts/` | Folder | Empty directory | Low |
| `docs/` | Folder | Empty directory (will be used or removed) | Low |
| `architecture/` | Folder | Empty directory (will be populated in Phase 5) | Low |

### Refactor / Consolidate

| Path | Action | Reason | Risk Level |
|------|--------|--------|------------|
| `app/alert_engine.py` | Refactor | Currently imports from `app.models` (obsolete) | Medium |
| `app/anomaly_detector.py` | Refactor | Check if it uses obsolete modules | Medium |

### Keep

| Path | Reason |
|------|--------|
| `app/main.py` | Main API entry point |
| `app/database/` | Modern database implementation |
| `app/services/` | Business logic |
| `app/routes/` | API routes |
| `dashboard/` | Streamlit dashboard |
| `requirements.txt` | Dependency management |
| `docker-compose.yml` | Container orchestration |
| `Dockerfile` | Backend containerization |

## Consolidation Plan

1. Update `app/alert_engine.py` to use `app.database.models` instead of `app.models`.
2. Update `app/anomaly_detector.py` to ensure it uses correct models.
3. Remove the obsolete files listed above.
4. Ensure `eventwatch.db` is added to `.gitignore`.
