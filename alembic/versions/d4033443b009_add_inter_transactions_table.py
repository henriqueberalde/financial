"""add inter transactions table

Revision ID: d4033443b009
Revises: 36c03bac0ff2
Create Date: 2022-11-03 05:57:30.797719

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'd4033443b009'
down_revision = '36c03bac0ff2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('inter_transactions',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('date',
                              mysql.DATETIME(),
                              nullable=False),
                    sa.Column('description',
                              mysql.VARCHAR(length=100),
                              nullable=False),
                    sa.Column('value',
                              mysql.DECIMAL(precision=15, scale=2),
                              nullable=False),
                    sa.Column('balance',
                              mysql.DECIMAL(precision=15, scale=2),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')
    op.create_index('id_UNIQUE', 'inter_transactions', ['id'], unique=True)


def downgrade() -> None:
    op.drop_table('inter_transactions')
