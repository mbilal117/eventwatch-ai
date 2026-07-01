"""Dependency injection and context management."""

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_database() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
