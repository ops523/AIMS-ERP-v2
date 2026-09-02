from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from database import SessionLocal
from services.seed_service import seed_database
from core.storage_manager import StorageManager


BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_INI = BASE_DIR / "alembic.ini"


def run_migrations():
    """
    Apply all pending Alembic migrations.

    Alembic remains the single source of truth for
    database schema creation and upgrades.
    """

    alembic_config = Config(
        str(ALEMBIC_INI)
    )

    command.upgrade(
        alembic_config,
        "head",
    )


def initialize_database():
    """
    Initialize application runtime dependencies.

    Startup order:

        Storage
            ↓
        Database migrations
            ↓
        Master-data seeding

    Schema management is handled exclusively by Alembic.
    """

    StorageManager.initialize()

    run_migrations()

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()
