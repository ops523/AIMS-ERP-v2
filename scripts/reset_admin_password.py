from __future__ import annotations

import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.startup import startup
from database import SessionLocal
from models.user import User
from utils.security import hash_password


def reset_admin_password() -> None:

    print()
    print("=" * 50)
    print("AIMS ERP - Admin Password Reset")
    print("=" * 50)
    print()

    startup()

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        if user is None:
            print("ERROR: Admin user does not exist.")
            return

        if not user.is_active:
            print("ERROR: Admin account is inactive.")
            return

        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print()

        password = getpass.getpass(
            "Enter new admin password: "
        )

        confirm_password = getpass.getpass(
            "Confirm new admin password: "
        )

        if not password:
            print("ERROR: Password cannot be empty.")
            return

        if password != confirm_password:
            print("ERROR: Passwords do not match.")
            return

        if len(password) < 8:
            print(
                "ERROR: Password must be at least 8 characters."
            )
            return

        user.password_hash = hash_password(password)

        db.commit()

        print()
        print("Admin password reset successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    reset_admin_password()
