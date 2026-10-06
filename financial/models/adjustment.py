import financial.database as db

from financial.models.transaction import Transaction
from sqlalchemy import Column, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship

transactions_adjustments = Table(
    'transactions_adjustments',
    db.Base.metadata,
    Column('adjustment_id', Integer, ForeignKey('adjustments.id')),
    Column('transaction_id', Integer, ForeignKey('transactions.id')),
)


class Adjustment(db.Base):
    __tablename__ = "adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reason = Column(String)

    transactions = relationship("Transaction",
                                secondary=transactions_adjustments,
                                backref="Adjustment")

    def gains(self) -> list[Transaction]:
        result: list[Transaction] = []
        for t in self.transactions:
            if t.is_gain():
                result.append(t)
        return result

    def spends(self) -> list[Transaction]:
        result: list[Transaction] = []
        for t in self.transactions:
            if t.is_spend():
                result.append(t)
        return result
