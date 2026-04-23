from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import AIConfigurationError
from app.services import AIService
from app.services import LeadService


def get_lead_service(db: Session = Depends(get_db)) -> LeadService:
    return LeadService(db)


def get_ai_service() -> AIService:
    try:
        return AIService()
    except AIConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
