from sqlalchemy import inspect

import models

from database import Base, engine
from config import DATABASE_URL


def initialize_database():

    print("=" * 70)
    print("DATABASE INITIALIZATION")
    print("=" * 70)

    print("DATABASE URL:", DATABASE_URL)

    print("\nRegistered models:")

    if not Base.metadata.tables:
        print(">>> NO MODELS REGISTERED <<<")
    else:
        for table in sorted(Base.metadata.tables.keys()):
            print(table)

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    print("\nTables in database:")

    tables = inspector.get_table_names()

    if not tables:
        print(">>> DATABASE HAS NO TABLES <<<")
    else:
        for table in tables:
            print(table)

    print("=" * 70)
