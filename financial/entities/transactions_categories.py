import financial.entities.db as db

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session


class TransactionsCategories(db.Base):
    __tablename__ = "transactions_categories"

    transaction_id = Column(Integer,
                            ForeignKey("transactions.id"),
                            primary_key=True)

    category_id = Column(Integer,
                         ForeignKey("categories.id"),
                         primary_key=True)

    category = relationship("Category")
    transaction = relationship("Transaction")

    @staticmethod
    def set_transactions_categories(session: Session):
        transactions_categories = session.query(TransactionsCategories).all()

        for tc in transactions_categories:
            tc.transaction.category_id = tc.category_id
            session.add(tc)

        session.commit()
