from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Response
from fastapi import status

from app.api.dependencies import get_ai_service
from app.api.dependencies import get_lead_service
from app.db.enums import LeadSource
from app.db.schemas import AISummaryRequest
from app.db.schemas import AISummaryResponse
from app.db.schemas import LeadCreate
from app.db.schemas import LeadListResponse
from app.db.schemas import LeadRead
from app.db.schemas import LeadStatsResponse
from app.db.schemas import LeadUpdate
from app.services import AIConfigurationError
from app.services import AIService
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


@router.post("/ai/summary", response_model=AISummaryResponse)
def get_ai_summary(
    payload: AISummaryRequest,
    lead_service: LeadService = Depends(get_lead_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AISummaryResponse:
    try:
        # Fetch up to 100 recent leads matching the filters to send to Gemini
        items, _ = lead_service.list_leads(
            page=1,
            limit=100,
            fuente=payload.fuente,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
        )

        used_filters = any(
            value is not None
            for value in (payload.fuente, payload.fecha_inicio, payload.fecha_fin)
        )
        fallback_note = ""
        if not items and used_filters:
            items, _ = lead_service.list_leads(
                page=1,
                limit=100,
                fuente=None,
                fecha_inicio=None,
                fecha_fin=None,
            )
            if items:
                fallback_note = (
                    "No se encontraron leads con los filtros indicados; "
                    "se genero el resumen con los leads mas recientes. "
                )
        
        # Serialize the subset of fields useful for AI analysis
        leads_data = [
            {
                "fuente": item.fuente.value,
                "producto_interes": item.producto_interes,
                "presupuesto": item.presupuesto,
                "creado": item.created_at.isoformat()
            }
            for item in items
        ]

        summary = ai_service.generate_leads_summary(leads_data)
        return AISummaryResponse(summary=f"{fallback_note}{summary}")
    except AIConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc



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
