from database import SessionLocal

from services.seed_service import seed_database
from core.storage_manager import StorageManager


def initialize_database():
    """
    Initialize application runtime dependencies.

    Database schema management is handled by Alembic.
    This function is responsible only for storage initialization
    and master-data seeding.
    """

    # Create storage folders
    StorageManager.initialize()

    # Seed master / initial application data
    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()