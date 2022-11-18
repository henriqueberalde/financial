"""add hash on inter transaction

Revision ID: e7317f182518
Revises: 9f35b5a74254
Create Date: 2022-11-18 10:29:49.390194

"""
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = 'e7317f182518'
down_revision = '9f35b5a74254'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "inter_transactions",
        Column("hash", mysql.VARCHAR(length=64), nullable=False)
    )
    op.add_column(
        "transactions",
        Column("original_hash", mysql.VARCHAR(length=64))
    )


def downgrade() -> None:
    op.drop_column(table_name="inter_transactions", column_name="hash")
    op.drop_column(table_name="transactions", column_name="original_hash")
