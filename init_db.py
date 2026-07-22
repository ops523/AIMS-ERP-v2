from database import Base
from database import engine

import models


def initialize_database():

    Base.metadata.create_all(bind=engine)
