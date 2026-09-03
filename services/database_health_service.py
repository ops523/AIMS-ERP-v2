from sqlalchemy import text

from config import (
    APP_ENV,
    DATABASE_IS_POSTGRES,
    DATABASE_IS_SQLITE,
    DATABASE_URL,
)


class DatabaseHealthService:

    @staticmethod
    def check_connection() -> bool:
        """
        Verify that the configured database is reachable.
        """

        from database import get_session

        db = get_session()

        try:
            db.execute(text("SELECT 1"))
            return True

        except Exception:
            return False

        finally:
            db.close()

    @staticmethod
    def get_database_type() -> str:
        """
        Return a human-readable database type.
        """

        if DATABASE_IS_POSTGRES:
            return "PostgreSQL"

        if DATABASE_IS_SQLITE:
            return "SQLite"

        return "Unknown"

    @staticmethod
    def validate_configuration() -> None:
        """
        Validate the configured database before application startup.

        Raises:
            RuntimeError: If the database configuration is unsupported.
        """

        if not DATABASE_URL:
            if APP_ENV == "production":
                raise RuntimeError(
                    "DATABASE_URL is required in production."
                )

            raise RuntimeError(
                "DATABASE_URL is not configured."
            )

        if APP_ENV == "production" and not DATABASE_IS_POSTGRES:
            raise RuntimeError(
                "Production environment requires "
                "a PostgreSQL DATABASE_URL."
            )

        if DATABASE_IS_POSTGRES:
            return

        if DATABASE_IS_SQLITE:
            return

        raise RuntimeError(
            "Unsupported database configuration. "
            "Use PostgreSQL or SQLite."
        )