from datetime import datetime

from sqlalchemy import func

from database import get_session


class AssetService:

    @staticmethod
    def next_number(model):

        session = get_session()

        try:

            count = session.query(

                func.count(model.id)

            ).scalar() or 0

            return count + 1

        finally:

            session.close()

    @staticmethod
    def generate(prefix, model):

        year = datetime.now().year

        number = AssetService.next_number(model)

        return f"{prefix}-{year}-{number:06d}"
