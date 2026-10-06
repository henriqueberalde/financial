import financial.database as db

from sqlalchemy import Column, Integer, String, DateTime, Numeric
from financial.importers.staging import StagedTransaction


class InterCreditCardTransaction(db.Base):
    """Staged line of an Inter credit card invoice."""
    __tablename__ = "inter_credit_card_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_month = Column(String)
    date = Column(DateTime)
    description = Column(String)
    category = Column(String)
    type = Column(String)
    value = Column(Numeric)
    hash = Column(String)

    def to_staged(self) -> StagedTransaction:
        return StagedTransaction(date=self.date,  # type: ignore
                                 description=self.description,  # type: ignore
                                 value=self.value,  # type: ignore
                                 balance=None,
                                 hash=self.hash)  # type: ignore
