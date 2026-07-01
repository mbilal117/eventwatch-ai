"""Log ingestion and retrieval routes."""

import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.log_service import LogService
from app.services.anomaly_service import AnomalyService
from app.services.alert_service import AlertService
from app.schemas.log_schemas import LogCreate, LogResponse, LogListResponse, LogFilterRequest, LogLevel, LogSource
from app.exceptions import FileProcessingException, LogIngestionException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/upload")
async def upload_logs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> dict:
    """Upload and ingest logs from a file (.log, .txt, or .csv)."""
    try:
        content = await file.read()
        logs_data = LogService.parse_log_file(content, file.filename)

        ingested_count = 0
        for log_dict in logs_data:
            timestamp_str = log_dict.get('timestamp', '')
            try:
                if isinstance(timestamp_str, str):
                    from datetime import datetime as dt
                    timestamp = dt.fromisoformat(timestamp_str) if timestamp_str else dt.utcnow()
                else:
                    timestamp = timestamp_str
            except (ValueError, TypeError):
                from datetime import datetime as dt
                timestamp = dt.utcnow()

            log_create = LogCreate(
                timestamp=timestamp,
                level=LogLevel(log_dict.get('level', 'INFO')),
                message=log_dict.get('message', ''),
                source=LogSource(log_dict.get('source', 'application')),
                service=log_dict.get('service', 'unknown'),
                metadata=log_dict.get('metadata'),
                file_source=file.filename,
                raw_line=log_dict.get('raw_line'),
            )

            log_entry = LogService.ingest_log(db, log_create)
            anomaly = AnomalyService.detect_anomaly(db, log_entry.id, log_entry)
            AlertService.detect_and_create_alerts(db, log_entry)
            ingested_count += 1

        logger.info(f"Successfully ingested {ingested_count} logs from {file.filename}")
        return {
            "success": True,
            "message": f"Successfully ingested {ingested_count} logs",
            "filename": file.filename,
            "count": ingested_count,
        }

    except FileProcessingException as e:
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/ingest")
async def ingest_single_log(
    log_data: LogCreate,
    db: Session = Depends(get_db)
) -> LogResponse:
    """Ingest a single log entry."""
    try:
        log_entry = LogService.ingest_log(db, log_data)
        anomaly = AnomalyService.detect_anomaly(db, log_entry.id, log_entry)
        AlertService.detect_and_create_alerts(db, log_entry)

        return LogResponse.model_validate(log_entry)

    except LogIngestionException as e:
        logger.error(f"Log ingestion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingest error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest log: {str(e)}")


@router.get("/", response_model=LogListResponse)
async def get_logs(
    level: Optional[LogLevel] = Query(None),
    source: Optional[LogSource] = Query(None),
    service: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> LogListResponse:
    """Get logs with filtering and pagination."""
    try:
        filters = LogFilterRequest(
            level=level,
            source=source,
            service=service,
            search_term=search_term,
            page=page,
            page_size=page_size,
        )

        logs, total = LogService.get_logs(db, filters)
        pages = (total + page_size - 1) // page_size

        return LogListResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            logs=logs,
        )

    except Exception as e:
        logger.error(f"Get logs error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    db: Session = Depends(get_db)
) -> LogResponse:
    """Get a specific log by ID."""
    try:
        log = LogService.get_log_by_id(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail=f"Log {log_id} not found")
        return log

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get log error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve log: {str(e)}")


@router.get("/statistics/summary")
async def get_log_statistics(db: Session = Depends(get_db)) -> dict:
    """Get log statistics."""
    try:
        stats = LogService.get_log_statistics(db)
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
