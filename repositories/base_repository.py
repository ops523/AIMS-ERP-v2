from __future__ import annotations

from typing import Type
from typing import TypeVar
from typing import Generic

from sqlalchemy.orm import Session

from models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):

    model: Type[T] = None

    @classmethod
    def get_by_id(
        cls,
        db: Session,
        id: int,
    ):

        return db.get(cls.model, id)

    @classmethod
    def get_all(
        cls,
        db: Session,
    ):

        return (
            db.query(cls.model)
            .all()
        )

    @classmethod
    def add(
        cls,
        db: Session,
        obj: T,
    ):

        db.add(obj)

        db.commit()

        db.refresh(obj)

        return obj

    @classmethod
    def update(
        cls,
        db: Session,
        obj: T,
    ):

        db.commit()

        db.refresh(obj)

        return obj

    @classmethod
    def delete(
        cls,
        db: Session,
        obj: T,
    ):

        db.delete(obj)

        db.commit()

    @classmethod
    def exists(
        cls,
        db: Session,
        id: int,
    ):

        return (
            db.get(cls.model, id)
            is not None
        )

    @classmethod
    def count(
        cls,
        db: Session,
    ):

        return (
            db.query(cls.model)
            .count()
        )
