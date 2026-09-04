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
        Validate the configured database and production
        application configuration before startup.

        Raises:
            RuntimeError: If the production configuration
            is invalid or unsupported.
        """

        from config import SECRET_KEY

        if not DATABASE_URL:
            if APP_ENV == "production":
                raise RuntimeError(
                    "DATABASE_URL is required in production."
                )

            raise RuntimeError(
                "DATABASE_URL is not configured."
            )

        if APP_ENV == "production":

            if not DATABASE_IS_POSTGRES:
                raise RuntimeError(
                    "Production environment requires "
                    "a PostgreSQL DATABASE_URL."
                )

            if not SECRET_KEY:
                raise RuntimeError(
                    "SECRET_KEY is required in production."
                )

            if SECRET_KEY == "dev-secret-key":
                raise RuntimeError(
                    "Production SECRET_KEY must not use "
                    "the default development secret."
                )

        if DATABASE_IS_POSTGRES:
            return

        if DATABASE_IS_SQLITE:
            return

        raise RuntimeError(
            "Unsupported database configuration. "
            "Use PostgreSQL or SQLite."
        )