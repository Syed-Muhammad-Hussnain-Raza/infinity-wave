"""Transcript processing service (Foundation stub).
Handles business logic for saving transcripts and creating entities.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.db.models import Transcript, User


def create_transcript_record(db: Session, raw_text: str, current_user: User) -> Transcript:
    """Save raw transcript record to persistent storage."""
    record = Transcript(
        raw_text=raw_text,
        created_by_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
