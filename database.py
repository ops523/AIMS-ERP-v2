from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models.base import Base


# ============================================================
# ENGINE CONFIGURATION
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine_kwargs = {
    "connect_args": connect_args,
}


# PostgreSQL production configuration
if DATABASE_URL.startswith("postgresql+psycopg"):
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        }
    )


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session():
    """
    Return a new SQLAlchemy database session.
    """
    return SessionLocal()