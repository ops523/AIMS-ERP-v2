from __future__ import annotations

from typing import Generic, TypeVar, Type, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):

    model: Type[T] = None

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    @classmethod
    def create(
        cls,
        db: Session,
        obj: T,
    ) -> T:

        db.add(obj)

        db.commit()

        db.refresh(obj)

        return obj

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    @classmethod
    def update(
        cls,
        db: Session,
        obj: T,
    ) -> T:

        db.commit()

        db.refresh(obj)

        return obj

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    @classmethod
    def get(
        cls,
        db: Session,
        object_id: int,
    ) -> Optional[T]:

        return (
            db.query(cls.model)
            .filter(cls.model.id == object_id)
            .first()
        )

    # ---------------------------------------------------------
    # GET BY UUID
    # ---------------------------------------------------------

    @classmethod
    def get_by_uuid(
        cls,
        db: Session,
        uuid: str,
    ) -> Optional[T]:

        if not hasattr(cls.model, "uuid"):

            return None

        return (
            db.query(cls.model)
            .filter(cls.model.uuid == uuid)
            .first()
        )

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    @classmethod
    def list(
        cls,
        db: Session,
        active_only: bool = False,
    ):

        query = db.query(cls.model)

        if active_only and hasattr(cls.model, "is_active"):

            query = query.filter(
                cls.model.is_active.is_(True)
            )

        if hasattr(cls.model, "created_at"):

            query = query.order_by(
                cls.model.created_at.desc()
            )

        return query.all()

    # ---------------------------------------------------------
    # COUNT
    # ---------------------------------------------------------

    @classmethod
    def count(
        cls,
        db: Session,
    ) -> int:

        return (
            db.query(
                func.count(cls.model.id)
            ).scalar()
            or 0
        )

    # ---------------------------------------------------------
    # EXISTS
    # ---------------------------------------------------------

    @classmethod
    def exists(
        cls,
        db: Session,
        object_id: int,
    ) -> bool:

        return cls.get(
            db,
            object_id,
        ) is not None

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    @classmethod
    def delete(
        cls,
        db: Session,
        obj: T,
    ):

        db.delete(obj)

        db.commit()

    # ---------------------------------------------------------
    # SOFT DELETE
    # ---------------------------------------------------------

    @classmethod
    def deactivate(
        cls,
        db: Session,
        obj: T,
    ):

        if hasattr(obj, "is_active"):

            obj.is_active = False

            db.commit()

            db.refresh(obj)

        return obj

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    @classmethod
    def paginate(
        cls,
        db: Session,
        page: int = 1,
        page_size: int = 20,
    ):

        query = db.query(cls.model)

        if hasattr(cls.model, "created_at"):

            query = query.order_by(
                cls.model.created_at.desc()
            )

        return (
            query.offset(
                (page - 1) * page_size
            )
            .limit(page_size)
            .all()
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    @classmethod
    def search(
        cls,
        db: Session,
        *filters,
    ):

        return (
            db.query(cls.model)
            .filter(*filters)
            .all()
        )
