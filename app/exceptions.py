"""Custom exceptions for EventWatch AI."""


class EventWatchException(Exception):
    """Base exception for EventWatch AI."""
    pass


class DatabaseException(EventWatchException):
    """Raised when database operations fail."""
    pass


class LogIngestionException(EventWatchException):
    """Raised when log ingestion fails."""
    pass


class ValidationException(EventWatchException):
    """Raised when validation fails."""
    pass


class AnomalyDetectionException(EventWatchException):
    """Raised when anomaly detection fails."""
    pass


class AlertException(EventWatchException):
    """Raised when alert operations fail."""
    pass


class WebhookException(EventWatchException):
    """Raised when webhook operations fail."""
    pass


class FileProcessingException(EventWatchException):
    """Raised when file processing fails."""
    pass
