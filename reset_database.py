from database import Base
from database import engine

import models


def reset():

    print("Dropping tables...")

    Base.metadata.drop_all(bind=engine)

    print("Creating tables...")

    Base.metadata.create_all(bind=engine)

    print("Database recreated successfully.")


if __name__ == "__main__":
    reset()
