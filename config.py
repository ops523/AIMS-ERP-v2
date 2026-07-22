from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR / 'aims.db'}"
)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key"
)

APP_NAME = "AIMS ERP"

COMPANY = "ADWALLZ"

VERSION = "2.0"
