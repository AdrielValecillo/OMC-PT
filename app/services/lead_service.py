from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.enums import LeadSource
from app.db.models import Lead
from app.db.repositories import LeadRepository
from app.db.schemas import LeadCreate
from app.db.schemas import LeadStatsResponse
from app.db.schemas import LeadUpdate


class LeadNotFoundError(Exception):
    pass


class DuplicateLeadEmailError(Exception):
    pass


class LeadService:
    def __init__(self, db: Session) -> None:
        self.repository = LeadRepository(db)

    def create_lead(self, payload: LeadCreate) -> Lead:
        if self.repository.get_by_email(payload.email):
            raise DuplicateLeadEmailError("El email ya existe")

        try:
            return self.repository.create(payload)
        except IntegrityError as exc:
            raise DuplicateLeadEmailError("El email ya existe") from exc

    def get_lead(self, lead_id: int) -> Lead:
        lead = self.repository.get_by_id(lead_id)
        if lead is None:
            raise LeadNotFoundError("Lead no encontrado")
        return lead

    def list_leads(
        self,
        page: int,
        limit: int,
        fuente: LeadSource | None,
        fecha_inicio: datetime | None,
        fecha_fin: datetime | None,
    ) -> tuple[list[Lead], int]:
        return self.repository.list_leads(page, limit, fuente, fecha_inicio, fecha_fin)

    def update_lead(self, lead_id: int, payload: LeadUpdate) -> Lead:
        lead = self.get_lead(lead_id)
        update_data = payload.model_dump(exclude_unset=True)

        new_email = update_data.get("email")
        if new_email and new_email != lead.email:
            existing = self.repository.get_by_email(new_email)
            if existing is not None:
                raise DuplicateLeadEmailError("El email ya existe")

        try:
            return self.repository.update(lead, payload)
        except IntegrityError as exc:
            raise DuplicateLeadEmailError("El email ya existe") from exc

    def delete_lead(self, lead_id: int) -> None:
        lead = self.get_lead(lead_id)
        self.repository.soft_delete(lead)

    def get_stats(self) -> LeadStatsResponse:
        total, leads_por_fuente, promedio, ultimos_7_dias = self.repository.stats()

        normalized_by_source = {
            source: leads_por_fuente.get(source, 0) for source in LeadSource
        }

        return LeadStatsResponse(
            total_leads=total,
            leads_por_fuente=normalized_by_source,
            promedio_presupuesto=Decimal(str(promedio)).quantize(Decimal("0.01")),
            leads_ultimos_7_dias=ultimos_7_dias,
        )
