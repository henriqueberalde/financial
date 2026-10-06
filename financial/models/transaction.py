import financial.database as db

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from typing import Iterable, Any
from financial.hashing import transaction_hash


class Transaction(db.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.original_value is None:
            self.original_value = self.value

        if self.original_hash is None:
            self.__generate_hash()

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    user_account = Column(String)
    bank = Column(String)
    date = Column(DateTime)
    description = Column(String)
    value = Column(Numeric)
    original_value = Column(Numeric)
    balance = Column(Numeric)
    category_id = Column(Numeric, ForeignKey("categories.id"))
    context = Column(String)
    original_hash = Column(String)

    category = relationship("Category")

    def is_spend(self) -> bool:
        return bool(self.value < 0)

    def is_gain(self) -> bool:
        return bool(self.value > 0)

    @staticmethod
    def set_context_of_many(session: Session,
                            ids: Iterable[Any] | str,
                            column_parm: str) -> None:

        ids_param = str(ids).split(" ") if isinstance(ids, str) else ids

        try:
            session.query(Transaction).filter(
                Transaction.id.in_(ids_param)
            ).update({
                Transaction.context: column_parm
            })
            session.commit()
        except Exception as e:
            print(f"Error while saving data to db.{e}")
            session.rollback()

    def __generate_hash(self) -> None:
        self.original_hash = transaction_hash(
            self.date, self.description, self.value, self.balance)  # type: ignore # nopep8
