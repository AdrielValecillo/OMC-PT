from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

from app.db.enums import LeadSource


class LeadCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=30)
    fuente: LeadSource
    producto_interes: str | None = Field(default=None, max_length=255)
    presupuesto: Decimal | None = Field(default=None, ge=0)


class LeadUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=30)
    fuente: LeadSource | None = None
    producto_interes: str | None = Field(default=None, max_length=255)
    presupuesto: Decimal | None = Field(default=None, ge=0)


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    fuente: LeadSource
    producto_interes: str | None
    presupuesto: Decimal | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    page: int
    limit: int
    total: int
    items: list[LeadRead]


class LeadStatsResponse(BaseModel):
    total_leads: int
    leads_por_fuente: dict[LeadSource, int]
    promedio_presupuesto: Decimal
    leads_ultimos_7_dias: int
