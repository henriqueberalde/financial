"""empty message

Revision ID: 6db917175025
Revises:
Create Date: 2022-10-29 19:32:50.523401

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6db917175025'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('categories',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('name',
                              mysql.VARCHAR(length=30),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')
    op.create_index('id_UNIQUE', 'categories', ['id'], unique=True)

    op.create_table('category_rules',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('category_id',
                              mysql.INTEGER(),
                              autoincrement=False, nullable=False),
                    sa.Column('rule',
                              mysql.VARCHAR(length=100),
                              nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(('category_id',),
                                            ['categories.id']),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')
    op.create_index('id_UNIQUE', 'category_rules', ['id'], unique=True)
    op.create_index('FK_category_id_categories_id_idx',
                    'category_rules',
                    ['category_id', 'id'],
                    unique=False)
    op.create_index('category_id_FK_idx',
                    'category_rules',
                    ['category_id'],
                    unique=False)

    op.create_table('transactions',
                    sa.Column('id',
                              mysql.INTEGER(),
                              autoincrement=True,
                              nullable=False),
                    sa.Column('user_id',
                              mysql.INTEGER(),
                              autoincrement=False,
                              nullable=False),
                    sa.Column('user_account',
                              mysql.VARCHAR(length=50),
                              nullable=False),
                    sa.Column('bank',
                              mysql.VARCHAR(length=10),
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
                    sa.Column('category_id',
                              mysql.INTEGER(),
                              autoincrement=False,
                              nullable=True),
                    sa.Column('context',
                              mysql.VARCHAR(length=50),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(('category_id',),
                                            ['categories.id']),
                    mysql_collate='utf8mb4_0900_ai_ci',
                    mysql_default_charset='utf8mb4',
                    mysql_engine='InnoDB')
    op.create_index('id_UNIQUE', 'transactions', ['id'], unique=True)
    op.create_index('FK_category_id_categories_id_idx',
                    'transactions',
                    ['category_id', 'id'],
                    unique=False)
    op.create_index('category_id_FK_idx',
                    'transactions',
                    ['category_id'],
                    unique=False)


def downgrade() -> None:
    op.drop_index('id_UNIQUE', table_name='categories')
    op.drop_table('categories')

    op.drop_index('id_UNIQUE', table_name='category_rules')
    op.drop_index('FK_category_id_categories_id_idx',
                  table_name='category_rules')
    op.drop_index('category_id_FK_idx', table_name='category_rules')
    op.drop_table('category_rules')

    op.drop_index('id_UNIQUE', table_name='transactions')
    op.drop_index('FK_category_id_categories_id_idx',
                  table_name='transactions')
    op.drop_index('category_id_FK_idx', table_name='transactions')
    op.drop_table('transactions')
