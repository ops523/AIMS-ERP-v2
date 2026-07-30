from database import Base
from database import engine
from database import SessionLocal

import models

from services.seed_service import seed_database

from core.storage_manager import StorageManager


def initialize_database():

    # Create storage folders

    StorageManager.initialize()

    # Create database tables

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        seed_database(db)

    finally:

        db.close()
