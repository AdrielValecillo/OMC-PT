from decimal import Decimal

from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.database import create_tables
from app.db.enums import LeadSource
from app.db.models import Lead


SEED_LEADS = [
    {
        "nombre": "Laura Gomez",
        "email": "laura.gomez@example.com",
        "telefono": "+573001112233",
        "fuente": LeadSource.instagram,
        "producto_interes": "Mentoria de ventas",
        "presupuesto": Decimal("450.00"),
    },
    {
        "nombre": "Andres Ruiz",
        "email": "andres.ruiz@example.com",
        "telefono": "+573004445566",
        "fuente": LeadSource.facebook,
        "producto_interes": "Curso de copywriting",
        "presupuesto": Decimal("320.00"),
    },
    {
        "nombre": "Camila Perez",
        "email": "camila.perez@example.com",
        "telefono": "+573007778899",
        "fuente": LeadSource.landing_page,
        "producto_interes": "Plantillas de embudo",
        "presupuesto": Decimal("210.00"),
    },
    {
        "nombre": "Julian Moreno",
        "email": "julian.moreno@example.com",
        "telefono": "+573009991122",
        "fuente": LeadSource.referido,
        "producto_interes": "Consultoria comercial",
        "presupuesto": Decimal("900.00"),
    },
    {
        "nombre": "Valentina Diaz",
        "email": "valentina.diaz@example.com",
        "telefono": "+573003334455",
        "fuente": LeadSource.otro,
        "producto_interes": "Automatizacion CRM",
        "presupuesto": Decimal("650.00"),
    },
    {
        "nombre": "Santiago Torres",
        "email": "santiago.torres@example.com",
        "telefono": "+573006661122",
        "fuente": LeadSource.instagram,
        "producto_interes": "Auditoria de funnel",
        "presupuesto": Decimal("500.00"),
    },
    {
        "nombre": "Natalia Rojas",
        "email": "natalia.rojas@example.com",
        "telefono": "+573001234567",
        "fuente": LeadSource.facebook,
        "producto_interes": "Entrenamiento de cierres",
        "presupuesto": Decimal("780.00"),
    },
    {
        "nombre": "Diego Herrera",
        "email": "diego.herrera@example.com",
        "telefono": "+573009876543",
        "fuente": LeadSource.landing_page,
        "producto_interes": "Sistema de lanzamientos",
        "presupuesto": Decimal("1200.00"),
    },
    {
        "nombre": "Maria Cardenas",
        "email": "maria.cardenas@example.com",
        "telefono": "+573005556677",
        "fuente": LeadSource.referido,
        "producto_interes": "Programa evergreen",
        "presupuesto": Decimal("540.00"),
    },
    {
        "nombre": "Felipe Castro",
        "email": "felipe.castro@example.com",
        "telefono": "+573002223344",
        "fuente": LeadSource.otro,
        "producto_interes": "Servicio de anuncios",
        "presupuesto": Decimal("390.00"),
    },
]


def run_seed() -> None:
    create_tables()
    session = SessionLocal()
    try:
        existing_emails = {email for email in session.scalars(select(Lead.email)).all()}

        leads_to_insert = [
            Lead(**payload)
            for payload in SEED_LEADS
            if payload["email"] not in existing_emails
        ]

        if not leads_to_insert:
            print("Seed omitido: no hay leads nuevos por insertar.")
            return

        session.add_all(leads_to_insert)
        session.commit()
        print(f"Seed completado: {len(leads_to_insert)} leads insertados.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
