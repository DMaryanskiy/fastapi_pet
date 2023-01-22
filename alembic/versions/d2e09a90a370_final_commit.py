"""Final commit

Revision ID: d2e09a90a370
Revises: aff2af5b6d6a
Create Date: 2023-01-22 12:19:11.873992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2e09a90a370'
down_revision = 'aff2af5b6d6a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    op.drop_table("test")
