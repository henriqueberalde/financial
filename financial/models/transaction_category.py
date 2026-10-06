import financial.database as db

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class TransactionCategory(db.Base):
    __tablename__ = "transactions_categories"

    transaction_id = Column(Integer,
                            ForeignKey("transactions.id"),
                            primary_key=True)

    category_id = Column(Integer,
                         ForeignKey("categories.id"),
                         primary_key=True)

    category = relationship("Category")
    transaction = relationship("Transaction")
