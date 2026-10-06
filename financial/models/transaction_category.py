import financial.database as db

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session


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

    @staticmethod
    def set_transactions_categories(session: Session):
        transactions_categories = session.query(TransactionCategory).all()

        for tc in transactions_categories:
            tc.transaction.category_id = tc.category_id
            session.add(tc)

        session.commit()

    @staticmethod
    def set_categories_by_user(session: Session) -> None:
        try:
            TransactionCategory.set_transactions_categories(session)
        except Exception as e:
            print(f"Error while setting specific categorization. {e}")
