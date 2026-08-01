"""
ERP Transaction Manager

Centralized transaction handling.

All business services should use this service instead of
calling commit()/rollback() directly.
"""

from contextlib import contextmanager

from sqlalchemy.orm import Session


class TransactionService:

    @staticmethod
    @contextmanager
    def transaction(db: Session):

        try:

            yield db

            db.commit()

        except Exception:

            db.rollback()

            raise
