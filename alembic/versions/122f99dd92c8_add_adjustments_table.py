"""add adjustments table

Revision ID: 122f99dd92c8
Revises: 14dab5a38d65
Create Date: 2022-11-17 08:30:33.167799

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '122f99dd92c8'
down_revision = '14dab5a38d65'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index('spend_id_gain_id_UNIQUE',
                  table_name='clearing_transactions')
    op.drop_table('clearing_transactions')

    op.create_table('adjustments',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('reason',
                              mysql.VARCHAR(length=150),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')

    op.create_table('transactions_adjustments',
                    sa.Column('adjustment_id',
                              mysql.INTEGER(),
                              nullable=False),
                    sa.Column('transaction_id',
                              mysql.INTEGER(),
                              nullable=False),
                    sa.PrimaryKeyConstraint('adjustment_id', 'transaction_id'),
                    sa.ForeignKeyConstraint(('adjustment_id',),
                                            ['adjustments.id']),
                    sa.ForeignKeyConstraint(('transaction_id',),
                                            ['transactions.id']),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')

    op.create_index('adjustment_id_transaction_id_UNIQUE',
                    'transactions_adjustments',
                    ['adjustment_id', 'transaction_id'],
                    unique=True)


def downgrade() -> None:
    op.drop_index('adjustment_id_transaction_id_UNIQUE',
                  table_name='transactions_adjustments')
    op.drop_table('transactions_adjustments')
    op.drop_table('adjustments')

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
