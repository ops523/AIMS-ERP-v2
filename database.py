from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

if DATABASE_URL.startswith("sqlite"):

    engine = create_engine(

        DATABASE_URL,

        connect_args={"check_same_thread": False},

        future=True

    )

else:

    engine = create_engine(

        DATABASE_URL,

        pool_pre_ping=True,

        future=True

    )

SessionLocal = sessionmaker(

    bind=engine,

    autoflush=False,

    autocommit=False,

    future=True

)

Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
