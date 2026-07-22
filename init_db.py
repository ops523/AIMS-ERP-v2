from database import Base, engine
import models


def initialize_database():
    Base.metadata.create_all(bind=engine)
