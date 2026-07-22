from database import engine
from models.base import Base

# Import all models
import models


def initialize_database():
    Base.metadata.create_all(bind=engine)
