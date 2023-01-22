"""Test

Revision ID: 8c0310c93581
Revises: 
Create Date: 2023-01-22 12:27:00.055882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c0310c93581'
down_revision = None
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
