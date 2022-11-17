"""add original value on transaction

Revision ID: 7abeabf21d60
Revises: 122f99dd92c8
Create Date: 2022-11-17 14:27:04.314405

"""
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = '7abeabf21d60'
down_revision = '122f99dd92c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column(table_name="transactions", column_name="calculated_value")
    op.add_column(
        "transactions",
        Column("original_value", mysql.DECIMAL(precision=15, scale=2)),
    )


def downgrade() -> None:
    op.drop_column(table_name="transactions", column_name="original_value")
    op.add_column(
        "transactions",
        Column("calculated_value", mysql.INTEGER()),
    )
