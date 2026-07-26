from database import Base
from database import engine

import traceback
import models


def initialize_database():

    print("=" * 60)
    print("Initializing database...")
    print("=" * 60)

    try:

        Base.metadata.create_all(bind=engine)

        print("SUCCESS")

    except Exception:

        traceback.print_exc()

        raise
