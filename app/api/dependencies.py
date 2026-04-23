from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import LeadService


def get_lead_service(db: Session = Depends(get_db)) -> LeadService:
    return LeadService(db)
