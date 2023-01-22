"""Test

Revision ID: ea3c4aa2955a
Revises: d2e09a90a370
Create Date: 2023-01-22 12:24:39.160483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea3c4aa2955a'
down_revision = 'd2e09a90a370'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "test",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("test", sa.String(50), unique=True)
    )


def downgrade() -> None:
    op.drop_table("test")
