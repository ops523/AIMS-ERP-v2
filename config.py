from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
).strip().lower()

if APP_ENV not in {
    "development",
    "production",
    "test",
}:
    raise RuntimeError(
        "Unsupported APP_ENV. "
        "Use development, production, or test."
    )


DATABASE_URL = os.getenv("DATABASE_URL")

# Local development / testing fallback
#
# SQLite fallback is intentionally allowed only outside
# production. Production must provide an explicit
# PostgreSQL DATABASE_URL.
if not DATABASE_URL and APP_ENV != "production":
    DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'aims.db'}"

if DATABASE_URL is None:
    DATABASE_URL = ""


# Normalize PostgreSQL URLs commonly provided by hosting platforms.
#
# postgres://...
# postgresql://...
#
# are converted to SQLAlchemy's psycopg driver format:
#
# postgresql+psycopg://...
#
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


# ============================================================
# DATABASE ENVIRONMENT
# ============================================================

DATABASE_IS_POSTGRES = DATABASE_URL.startswith(
    "postgresql+psycopg://"
)

DATABASE_IS_SQLITE = DATABASE_URL.startswith(
    "sqlite:///"
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key",
)

APP_NAME = os.getenv(
    "APP_NAME",
    "AIMS ERP",
)

COMPANY = os.getenv(
    "COMPANY",
    "ADWALLZ",
)

VERSION = os.getenv(
    "APP_VERSION",
    "2.0",
)
