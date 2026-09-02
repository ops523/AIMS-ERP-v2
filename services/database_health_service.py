from sqlalchemy import text

from database import get_session


class DatabaseHealthService:

    @staticmethod
    def check_connection() -> bool:
        db = get_session()

        try:
            db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
        finally:
            db.close()