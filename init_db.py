from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from services.seed_service import seed_database
from services.database_health_service import DatabaseHealthService
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
        Configuration validation
            ↓
        Database migrations
            ↓
        Database health check
            ↓
        Master-data seeding

    Schema management is handled exclusively by Alembic.
    """

    StorageManager.initialize()

    # Validate configuration before importing database.py.
    #
    # This is important in production because database.py
    # creates the SQLAlchemy engine at import time.
    DatabaseHealthService.validate_configuration()

    run_migrations()

    if not DatabaseHealthService.check_connection():
        raise RuntimeError(
            "Database health check failed after migrations."
        )

    # Import only after configuration validation and
    # successful database initialization.
    from database import SessionLocal

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()