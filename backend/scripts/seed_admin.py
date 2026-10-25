"""Create an initial admin account for local development."""

import os
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Role, User
from app.core.security import PasswordHasher
from app.db.session import _get_engine


def seed_admin() -> None:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")

    if not email or not password:
        sys.exit("Set ADMIN_EMAIL and ADMIN_PASSWORD before running this script.")

    if len(password) < 12:
        sys.exit("ADMIN_PASSWORD must contain at least 12 characters.")

    with Session(_get_engine()) as session:
        existing_user = session.scalar(select(User).where(User.email == email))

        if existing_user is not None:
            if existing_user.role == Role.admin:
                print(f"Admin account {email} already exists; no changes made.")
                return

            sys.exit(
                f"Account {email} already exists as a customer. "
                "No changes made; use a different email or promote the "
                "account through an explicitly authorized process."
            )

        admin = User(
            email=email,
            hashed_password=PasswordHasher().hash(password),
            role=Role.admin,
        )

        session.add(admin)

        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

        print(f"Admin account {email} created successfully.")


if __name__ == "__main__":
    seed_admin()
