import financial.entities.db as db
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from typing import Iterable, List, Any


class Transaction(db.Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    user_account = Column(String)
    bank = Column(String)
    date = Column(DateTime)
    description = Column(String)
    value = Column(Numeric)
    balance = Column(Numeric)
    category_id = Column(Numeric, ForeignKey("categories.id"))
    context = Column(String)

    category = relationship("Category")

    @staticmethod
    def set_context_of_many(session: Session,
                            ids: Iterable[Any] | str,
                            column_parm: str) -> None:

        ids_param = str(ids).split(" ") if type(ids) == str else ids

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
