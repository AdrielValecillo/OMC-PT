from app.db.database import SessionLocal
from app.db.database import create_tables
from app.db.models import Lead
from scripts.seed_leads import run_seed


def test_seed_is_idempotent() -> None:
    create_tables()

    run_seed()
    first_session = SessionLocal()
    try:
        first_count = first_session.query(Lead).count()
    finally:
        first_session.close()

    run_seed()
    second_session = SessionLocal()
    try:
        second_count = second_session.query(Lead).count()
    finally:
        second_session.close()

    assert first_count >= 10
    assert first_count == second_count
