from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Response
from fastapi import status

from app.api.dependencies import get_lead_service
from app.db.enums import LeadSource
from app.db.schemas import LeadCreate
from app.db.schemas import LeadListResponse
from app.db.schemas import LeadRead
from app.db.schemas import LeadStatsResponse
from app.db.schemas import LeadUpdate
from app.services import DuplicateLeadEmailError
from app.services import LeadNotFoundError
from app.services import LeadService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    service: LeadService = Depends(get_lead_service),
) -> LeadRead:
    try:
        lead = service.create_lead(payload)
        return LeadRead.model_validate(lead)
    except DuplicateLeadEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("", response_model=LeadListResponse)
def list_leads(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    fuente: LeadSource | None = Query(default=None),
    fecha_inicio: datetime | None = Query(default=None),
    fecha_fin: datetime | None = Query(default=None),
    service: LeadService = Depends(get_lead_service),
) -> LeadListResponse:
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_inicio no puede ser mayor que fecha_fin",
        )

    items, total = service.list_leads(page, limit, fuente, fecha_inicio, fecha_fin)
    return LeadListResponse(
        page=page,
        limit=limit,
        total=total,
        items=[LeadRead.model_validate(item) for item in items],
    )


@router.get("/stats", response_model=LeadStatsResponse)
def get_stats(service: LeadService = Depends(get_lead_service)) -> LeadStatsResponse:
    return service.get_stats()


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(
    lead_id: int,
    service: LeadService = Depends(get_lead_service),
) -> LeadRead:
    try:
        lead = service.get_lead(lead_id)
        return LeadRead.model_validate(lead)
    except LeadNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{lead_id}", response_model=LeadRead)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    service: LeadService = Depends(get_lead_service),
) -> LeadRead:
    try:
        lead = service.update_lead(lead_id, payload)
        return LeadRead.model_validate(lead)
    except LeadNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateLeadEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    service: LeadService = Depends(get_lead_service),
) -> Response:
    try:
        service.delete_lead(lead_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LeadNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
