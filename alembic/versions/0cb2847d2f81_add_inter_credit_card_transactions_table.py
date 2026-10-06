"""add inter credit card transactions table

Staging table for the Banco Inter credit card invoices, merged into
transactions one invoice month at a time.

Revision ID: 0cb2847d2f81
Revises: dd7f1829ec89
Create Date: 2026-10-06 16:05:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '0cb2847d2f81'
down_revision = 'dd7f1829ec89'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('inter_credit_card_transactions',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('invoice_month',
                              mysql.VARCHAR(length=7),
                              nullable=False),
                    sa.Column('date',
                              mysql.DATETIME(),
                              nullable=False),
                    sa.Column('description',
                              mysql.VARCHAR(length=255),
                              nullable=False),
                    sa.Column('category',
                              mysql.VARCHAR(length=50),
                              nullable=True),
                    sa.Column('type',
                              mysql.VARCHAR(length=30),
                              nullable=True),
                    sa.Column('value',
                              mysql.DECIMAL(precision=15, scale=2),
                              nullable=False),
                    sa.Column('hash',
                              mysql.VARCHAR(length=64),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')
    op.create_index('invoice_month_idx',
                    'inter_credit_card_transactions',
                    ['invoice_month'])


def downgrade() -> None:
    op.drop_table('inter_credit_card_transactions')
