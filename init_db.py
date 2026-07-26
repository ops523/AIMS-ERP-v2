from sqlalchemy import inspect

import models

from database import Base, engine


def initialize_database():
    Base.metadata.create_all(bind=engine)
