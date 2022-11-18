"""add sector on categories table


Revision ID: 9f35b5a74254
Revises: 7abeabf21d60
Create Date: 2022-11-18 07:32:03.083424

"""
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import Column


# revision identifiers, used by Alembic.
revision = '9f35b5a74254'
down_revision = '7abeabf21d60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "categories",
        Column("sector", mysql.VARCHAR(length=30)),
    )


def downgrade() -> None:
    op.drop_column(table_name="categories", column_name="sector")
