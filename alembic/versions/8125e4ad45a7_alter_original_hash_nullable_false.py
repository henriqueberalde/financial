"""alter original hash nullable false

Revision ID: 8125e4ad45a7
Revises: e7317f182518
Create Date: 2022-11-18 11:12:15.832326

"""
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '8125e4ad45a7'
down_revision = 'e7317f182518'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "transactions",
        "original_hash",
        existing_type=mysql.VARCHAR(length=64),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column("transactions", "original_hash", nullable=True)
