"""add_roles_and_role_id_to_users

Revision ID: fc8ebc1f72e6
Revises: 35b941d7c146
Create Date: 2026-05-16 10:18:12.631398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc8ebc1f72e6'
down_revision: Union[str, Sequence[str], None] = '35b941d7c146'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=50), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('level', name='uq_roles_level'),
    sa.UniqueConstraint('slug', name='uq_roles_slug')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)

    bind = op.get_bind()
    bind.execute(sa.text(
        "INSERT INTO roles (id, name, slug, level) VALUES "
        "(1, 'Master', 'master', 1), "
        "(2, 'Admin', 'admin', 2), "
        "(3, 'User', 'user', 3)"
    ))

    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_users_role_id'), 'users', ['role_id'], unique=False)
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    op.execute(sa.text("UPDATE users SET role_id = 3 WHERE role_id IS NULL"))
    op.alter_column('users', 'role_id', existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_role_id'), table_name='users')
    op.drop_column('users', 'role_id')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
