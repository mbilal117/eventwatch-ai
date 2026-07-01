"""Log ingestion and processing service."""

import logging
import csv
import io
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.database.models import Log
from app.schemas.log_schemas import LogCreate, LogResponse, LogFilterRequest
from app.exceptions import LogIngestionException, FileProcessingException

logger = logging.getLogger(__name__)


class LogService:
    """Service for log ingestion and retrieval."""

    @staticmethod
    def ingest_log(db: Session, log_data: LogCreate) -> Log:
        """Ingest a single log entry."""
        try:
            log_entry = Log(
                timestamp=log_data.timestamp,
                level=log_data.level.value,
                message=log_data.message,
                source=log_data.source.value,
                service=log_data.service,
                metadata_json=log_data.metadata,
                file_source=log_data.file_source,
                raw_line=log_data.raw_line,
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            logger.info(f"Log ingested: {log_entry.id}")
            return log_entry
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to ingest log: {str(e)}")
            raise LogIngestionException(f"Failed to ingest log: {str(e)}")

    @staticmethod
    def parse_log_file(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Parse log file (.log, .txt, or .csv)."""
        try:
            if filename.endswith('.csv'):
                return LogService._parse_csv(file_content)
            elif filename.endswith(('.log', '.txt')):
                return LogService._parse_text(file_content, filename)
            else:
                raise FileProcessingException(f"Unsupported file type: {filename}")
        except Exception as e:
            logger.error(f"Failed to parse file {filename}: {str(e)}")
            raise FileProcessingException(f"Failed to parse file: {str(e)}")

    @staticmethod
    def _parse_csv(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV log file."""
        logs = []
        content_str = file_content.decode('utf-8', errors='ignore')
        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)

        for row in reader:
            logs.append({
                'timestamp': row.get('timestamp', datetime.utcnow().isoformat()),
                'level': row.get('level', 'INFO').upper(),
                'message': row.get('message', ''),
                'source': row.get('source', 'application'),
                'service': row.get('service', 'unknown'),
                'raw_line': str(row),
            })
        return logs

    @staticmethod
    def _parse_text(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Parse text log file."""
        logs = []
        content_str = file_content.decode('utf-8', errors='ignore')
        lines = content_str.split('\n')

        for line in lines:
            if not line.strip():
                continue

            log_dict = LogService._extract_log_info(line, filename)
            logs.append(log_dict)

        return logs

    @staticmethod
    def _extract_log_info(line: str, filename: str) -> Dict[str, Any]:
        """Extract log information from a line."""
        level = 'INFO'
        for lvl in ['ERROR', 'CRITICAL', 'WARNING', 'DEBUG']:
            if lvl in line.upper():
                level = lvl
                break

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': line[:2000],
            'source': 'application',
            'service': filename.replace('.log', '').replace('.txt', ''),
            'raw_line': line,
        }

    @staticmethod
    def get_logs(db: Session, filters: LogFilterRequest) -> Tuple[List[LogResponse], int]:
        """Get logs with filtering and pagination."""
        query = db.query(Log)

        if filters.level:
            query = query.filter(Log.level == filters.level.value)
        if filters.source:
            query = query.filter(Log.source == filters.source.value)
        if filters.service:
            query = query.filter(Log.service.ilike(f"%{filters.service}%"))
        if filters.start_date:
            query = query.filter(Log.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(Log.timestamp <= filters.end_date)
        if filters.search_term:
            query = query.filter(Log.message.ilike(f"%{filters.search_term}%"))

        total = query.count()
        offset = (filters.page - 1) * filters.page_size
        logs = query.order_by(desc(Log.timestamp)).offset(offset).limit(filters.page_size).all()

        responses = [LogResponse.model_validate(log) for log in logs]
        return responses, total

    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[LogResponse]:
        """Get a single log by ID."""
        log = db.query(Log).filter(Log.id == log_id).first()
        return LogResponse.model_validate(log) if log else None

    @staticmethod
    def delete_old_logs(db: Session, days: int = 30) -> int:
        """Delete logs older than specified days."""
        try:
            cutoff_date = datetime.utcnow()
            cutoff_date = cutoff_date.replace(
                day=cutoff_date.day - days
            ) if cutoff_date.day > days else datetime(cutoff_date.year, 1, 1)

            query = db.query(Log).filter(Log.timestamp < cutoff_date)
            count = query.delete()
            db.commit()
            logger.info(f"Deleted {count} old logs")
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete old logs: {str(e)}")
            raise LogIngestionException(f"Failed to delete old logs: {str(e)}")

    @staticmethod
    def get_log_statistics(db: Session) -> Dict[str, Any]:
        """Get log statistics."""
        total_logs = db.query(Log).count()
        level_counts = {}
        for log in db.query(Log.level).distinct():
            count = db.query(Log).filter(Log.level == log[0]).count()
            level_counts[log[0]] = count

        source_counts = {}
        for log in db.query(Log.source).distinct():
            count = db.query(Log).filter(Log.source == log[0]).count()
            source_counts[log[0]] = count

        return {
            'total_logs': total_logs,
            'by_level': level_counts,
            'by_source': source_counts,
        }
