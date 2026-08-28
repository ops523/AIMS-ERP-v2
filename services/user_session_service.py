from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models.user import User
from models.user_session import UserSession


SESSION_DAYS = 7


class UserSessionService:

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def create(
        db: Session,
        user: User,
        days: int = SESSION_DAYS,
    ) -> str:

        now = datetime.utcnow()

        token = secrets.token_urlsafe(48)

        session = UserSession(
            user_id=user.id,
            token_hash=UserSessionService._hash_token(token),
            expires_at=now + timedelta(days=days),
            last_seen_at=now,
            is_active=True,
        )

        db.add(session)
        db.commit()

        return token

    @staticmethod
    def get_user(
        db: Session,
        token: str | None,
    ) -> User | None:

        if not token:
            return None

        token_hash = UserSessionService._hash_token(token)

        session = (
            db.query(UserSession)
            .filter(
                UserSession.token_hash == token_hash,
                UserSession.is_active.is_(True),
            )
            .first()
        )

        if session is None:
            return None

        now = datetime.utcnow()

        if session.expires_at <= now:
            session.is_active = False
            db.commit()
            return None

        user = (
            db.query(User)
            .filter(
                User.id == session.user_id,
                User.is_active.is_(True),
            )
            .first()
        )

        if user is None:
            session.is_active = False
            db.commit()
            return None

        session.last_seen_at = now
        db.commit()

        return user

    @staticmethod
    def invalidate(
        db: Session,
        token: str | None,
    ) -> None:

        if not token:
            return

        token_hash = UserSessionService._hash_token(token)

        session = (
            db.query(UserSession)
            .filter(
                UserSession.token_hash == token_hash,
            )
            .first()
        )

        if session is not None:
            session.is_active = False
            db.commit()

    @staticmethod
    def invalidate_all_for_user(
        db: Session,
        user_id: int,
    ) -> None:

        (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_active.is_(True),
            )
            .update(
                {
                    UserSession.is_active: False,
                },
                synchronize_session=False,
            )
        )

        db.commit()
