"""Add clearing transactions

Revision ID: 07ddbe6c2163
Revises: d4033443b009
Create Date: 2022-11-16 11:54:56.631199

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '07ddbe6c2163'
down_revision = 'd4033443b009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('clearing_transactions',
                    sa.Column('spend_id',
                              mysql.INTEGER(),
                              nullable=False),
                    sa.Column('gain_id',
                              mysql.INTEGER(),
                              nullable=False),
                    sa.PrimaryKeyConstraint('spend_id', 'gain_id'),
                    sa.ForeignKeyConstraint(('spend_id',),
                                            ['transactions.id']),
                    sa.ForeignKeyConstraint(('gain_id',),
                                            ['transactions.id']),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')

    op.create_index('spend_id_gain_id_UNIQUE',
                    'clearing_transactions',
                    ['spend_id', 'gain_id'],
                    unique=True)


def downgrade() -> None:
    op.drop_index('spend_id_gain_id_UNIQUE',
                  table_name='clearing_transactions')
    op.drop_table('clearing_transactions')
