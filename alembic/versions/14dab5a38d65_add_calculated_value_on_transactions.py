"""add calculated value on transactions

Revision ID: 14dab5a38d65
Revises: 07ddbe6c2163
Create Date: 2022-11-16 12:03:32.764519

"""
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = '14dab5a38d65'
down_revision = '07ddbe6c2163'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        Column("calculated_value", mysql.INTEGER()),
    )


def downgrade() -> None:
    op.drop_column(table_name="transactions", column_name="calculated_value")
