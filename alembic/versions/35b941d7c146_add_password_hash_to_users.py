"""add_password_hash_to_users

Revision ID: 35b941d7c146
Revises: f3646b21b936
Create Date: 2026-05-16 10:01:13.311685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35b941d7c146'
down_revision: Union[str, Sequence[str], None] = 'f3646b21b936'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("users")}

    if "password_hash" not in column_names:
        op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))

    op.execute(sa.text("UPDATE users SET password_hash = 'reset_required' WHERE password_hash IS NULL"))
    op.alter_column('users', 'password_hash', existing_type=sa.String(length=255), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("users")}

    if "password_hash" in column_names:
        op.drop_column('users', 'password_hash')
