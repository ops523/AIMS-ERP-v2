from sqlalchemy import inspect

from database import Base, engine
import models


def initialize_database():
    print("=" * 60)
    print("REGISTERED MODELS")
    print("=" * 60)

    for table in sorted(Base.metadata.tables.keys()):
        print(table)

    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("DATABASE TABLES")
    print("=" * 60)

    inspector = inspect(engine)

    for table in inspector.get_table_names():
        print(table)
