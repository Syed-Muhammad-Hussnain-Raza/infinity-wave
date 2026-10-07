from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.transcript import TranscriptInput, TranscriptProcessResponse
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])


@router.post("/process", response_model=TranscriptProcessResponse, status_code=status.HTTP_200_OK)
def process_transcript(
    input_data: TranscriptInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Transcript AI parsing endpoint (Admin only - to be hooked to OpenRouter)."""
    return {
        "message": "AI Transcript processor ready for OpenRouter integration.",
        "projects": [],
    }
