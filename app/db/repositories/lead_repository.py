from datetime import UTC
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import Select
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.enums import LeadSource
from app.db.models import Lead
from app.db.schemas import LeadCreate
from app.db.schemas import LeadUpdate


class LeadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: LeadCreate) -> Lead:
        lead = Lead(**payload.model_dump())
        self.db.add(lead)
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        self.db.refresh(lead)
        return lead

    def get_by_email(self, email: str) -> Lead | None:
        query = self._active_leads_query().where(Lead.email == email)
        return self.db.scalar(query)

    def get_by_id(self, lead_id: int) -> Lead | None:
        query = self._active_leads_query().where(Lead.id == lead_id)
        return self.db.scalar(query)

    def list_leads(
        self,
        page: int,
        limit: int,
        fuente: LeadSource | None,
        fecha_inicio: datetime | None,
        fecha_fin: datetime | None,
    ) -> tuple[list[Lead], int]:
        query = self._active_leads_query()

        if fuente is not None:
            query = query.where(Lead.fuente == fuente)

        if fecha_inicio is not None:
            query = query.where(Lead.created_at >= fecha_inicio)

        if fecha_fin is not None:
            query = query.where(Lead.created_at <= fecha_fin)

        total_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(total_query) or 0

        offset = (page - 1) * limit
        paginated_query = (
            query.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        )
        items = list(self.db.scalars(paginated_query).all())
        return items, total

    def update(self, lead: Lead, payload: LeadUpdate) -> Lead:
        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(lead, field_name, field_value)

        self.db.add(lead)
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        self.db.refresh(lead)
        return lead

    def soft_delete(self, lead: Lead) -> None:
        lead.deleted_at = datetime.now(UTC)
        self.db.add(lead)
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def stats(self) -> tuple[int, dict[LeadSource, int], Decimal, int]:
        total_query = select(func.count(Lead.id)).where(Lead.deleted_at.is_(None))
        total_leads = self.db.scalar(total_query) or 0

        source_query = (
            select(Lead.fuente, func.count(Lead.id))
            .where(Lead.deleted_at.is_(None))
            .group_by(Lead.fuente)
        )
        leads_por_fuente: dict[LeadSource, int] = {
            fuente: count for fuente, count in self.db.execute(source_query).all()
        }

        avg_query = select(func.avg(Lead.presupuesto)).where(Lead.deleted_at.is_(None))
        avg_value = self.db.scalar(avg_query)
        promedio_presupuesto = Decimal(str(avg_value or 0)).quantize(Decimal("0.01"))

        seven_days_ago = datetime.now(UTC) - timedelta(days=7)
        recent_query = select(func.count(Lead.id)).where(
            Lead.deleted_at.is_(None),
            Lead.created_at >= seven_days_ago,
        )
        leads_ultimos_7_dias = self.db.scalar(recent_query) or 0

        return total_leads, leads_por_fuente, promedio_presupuesto, leads_ultimos_7_dias

    @staticmethod
    def _active_leads_query() -> Select[tuple[Lead]]:
        return select(Lead).where(Lead.deleted_at.is_(None))
