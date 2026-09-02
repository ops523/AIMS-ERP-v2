from sqlalchemy import text

from database import get_session


class DatabaseHealthService:

    @staticmethod
    def check_connection() -> bool:
        """
        Verify that the configured database is reachable.
        """

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

        from config import DATABASE_IS_POSTGRES, DATABASE_IS_SQLITE

        if DATABASE_IS_POSTGRES:
            return "PostgreSQL"

        if DATABASE_IS_SQLITE:
            return "SQLite"

        return "Unknown"