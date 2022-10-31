"""add transactions_categories table

Revision ID: 36c03bac0ff2
Revises: 6db917175025
Create Date: 2022-10-31 11:02:04.805094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '36c03bac0ff2'
down_revision = '6db917175025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('transactions_categories',
                    sa.Column('transaction_id',
                              mysql.INTEGER(),
                              nullable=False),
                    sa.Column('category_id',
                              mysql.INTEGER(),
                              autoincrement=False,
                              nullable=False),
                    sa.PrimaryKeyConstraint('transaction_id', 'category_id'),
                    sa.ForeignKeyConstraint(('transaction_id',),
                                            ['transactions.id']),
                    sa.ForeignKeyConstraint(('category_id',),
                                            ['categories.id']),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')

    op.create_index('transaction_id_category_id_UNIQUE',
                    'transactions_categories',
                    ['transaction_id', 'category_id'],
                    unique=True)


def downgrade() -> None:
    op.drop_index('transaction_id_category_id_UNIQUE',
                  table_name='transactions_categories')
    op.drop_table('transactions_categories')
