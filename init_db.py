from database import Base
from database import engine
from database import SessionLocal

import models

from services.seed_service import seed_database


def initialize_database():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()
