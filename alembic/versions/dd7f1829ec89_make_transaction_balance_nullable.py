"""make transaction balance nullable

Credit card purchases do not change the checking account balance, so
their transactions have no balance.

Revision ID: dd7f1829ec89
Revises: 3b9f1c2d7e8a
Create Date: 2026-10-06 16:00:00.000000

"""
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'dd7f1829ec89'
down_revision = '3b9f1c2d7e8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("transactions",
                    "balance",
                    existing_type=mysql.DECIMAL(precision=15, scale=2),
                    nullable=True)


def downgrade() -> None:
    # Fails while transactions without balance exist
    op.alter_column("transactions",
                    "balance",
                    existing_type=mysql.DECIMAL(precision=15, scale=2),
                    nullable=False)
