from sqlalchemy import inspect

from database import Base, engine
import models


def initialize_database():
    print("=" * 60)
    print("INITIALIZING DATABASE")
    print("=" * 60)

    print("\nRegistered Models:")
    for table in sorted(Base.metadata.tables.keys()):
        print(f" - {table}")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    print("\nActual Database Tables:")
    for table in sorted(inspector.get_table_names()):
        print(f" - {table}")

    print("\nDatabase initialization completed.")
