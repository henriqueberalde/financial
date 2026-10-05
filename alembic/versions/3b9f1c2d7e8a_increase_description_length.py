"""increase description length

Revision ID: 3b9f1c2d7e8a
Revises: 8125e4ad45a7
Create Date: 2026-10-05 18:00:00.000000

"""
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '3b9f1c2d7e8a'
down_revision = '8125e4ad45a7'
branch_labels = None
depends_on = None

tables = ["inter_transactions", "transactions"]


def upgrade() -> None:
    for table in tables:
        op.alter_column(
            table,
            "description",
            existing_type=mysql.VARCHAR(length=100),
            type_=mysql.VARCHAR(length=255),
            existing_nullable=False
        )


def downgrade() -> None:
    for table in tables:
        op.alter_column(
            table,
            "description",
            existing_type=mysql.VARCHAR(length=255),
            type_=mysql.VARCHAR(length=100),
            existing_nullable=False
        )
