import financial.database as db

from sqlalchemy import Column, Integer, String, DateTime, Numeric
from financial.hashing import transaction_hash
from financial.importers.staging import StagedTransaction


class InterTransaction(db.Base):
    __tablename__ = "inter_transactions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.hash is None:
            self.__generate_hash()

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    description = Column(String)
    value = Column(Numeric)
    balance = Column(Numeric)
    hash = Column(String)

    def __generate_hash(self) -> None:
        self.hash = transaction_hash(
            self.date, self.description, self.value, self.balance)  # type: ignore # nopep8

    def to_staged(self) -> StagedTransaction:
        return StagedTransaction(date=self.date,  # type: ignore
                                 description=self.description,  # type: ignore
                                 value=self.value,  # type: ignore
                                 balance=self.balance,  # type: ignore
                                 hash=self.hash)  # type: ignore
