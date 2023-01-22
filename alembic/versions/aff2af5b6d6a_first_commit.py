"""First commit

Revision ID: aff2af5b6d6a
Revises: 
Create Date: 2023-01-22 11:54:17.486062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aff2af5b6d6a'
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
    pass
