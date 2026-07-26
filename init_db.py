from sqlalchemy import inspect

import models

from database import Base
from database import engine


def initialize_database():

    print("=" * 70)
    print("AIMS ERP DATABASE INITIALIZATION")
    print("=" * 70)

    print("\nRegistered Models")

    for table in sorted(Base.metadata.tables.keys()):
        print(" -", table)

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    print("\nDatabase Tables")

    for table in sorted(inspector.get_table_names()):
        print(" -", table)

    print("\nInitialization Complete")
