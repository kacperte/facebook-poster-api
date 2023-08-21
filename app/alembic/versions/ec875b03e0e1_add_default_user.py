"""Add default user

Revision ID: ec875b03e0e1
Revises: 
Create Date: 2023-08-15 10:29:48.388490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ec875b03e0e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import context
    import os
    from db.database import SessionLocal
    from db.db_user import create_user
    from schemas import UserBase

    def read_secret(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()

    secrets_dir = '/etc/user-secrets/'

    with SessionLocal() as db:
        connection = context.get_bind()
        result = connection.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'kacper.trzepiecinski@hsswork.pl'"
        ).fetchone()
        if result[0] == 0:
            default_user = UserBase(
                username=read_secret(f"{secrets_dir}username"),
                password=read_secret(f"{secrets_dir}password"),
                email=read_secret(f"{secrets_dir}email")
            )
            create_user(db=db, request=default_user)




