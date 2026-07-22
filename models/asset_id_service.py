from datetime import datetime

from sqlalchemy import func

from database import get_session


class AssetIDService:

    @staticmethod
    def generate(model, prefix: str):

        session = get_session()

        try:

            year = datetime.now().year

            count = session.query(
                func.count(model.id)
            ).scalar() or 0

            count += 1

            return f"{prefix}-{year}-{count:06d}"

        finally:

            session.close()
