from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.transcript import TranscriptProcessRequest, TranscriptProcessResponse
from app.services.transcript_service import process_and_save_transcript
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])


@router.post("/process", response_model=TranscriptProcessResponse, status_code=status.HTTP_200_OK)
def process_transcript_endpoint(
    request: TranscriptProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only endpoint to process a meeting transcript via Gemini AI,
    validate extracted projects and tasks, and persist them atomically.
    """
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty",
        )

    result = process_and_save_transcript(db, request.transcript, current_user)
    return result
