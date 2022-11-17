import financial.entities.db as db

from financial.entities.transaction import Transaction
from sqlalchemy import Column, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship, Session

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

    @staticmethod
    def add(session: Session,
            reason: str,
            transactions: list[int] | list[Transaction]):

        t_normalized = Adjustment.__normalize_and_validate(
            session,
            transactions
        )

        try:
            adjustment = Adjustment(reason=reason)

            for t in t_normalized:
                adjustment.transactions.append(t)

            session.add(adjustment)

            gains = adjustment.gains()
            spends = adjustment.spends()

            spends.sort(
                reverse=True,
                key=lambda t: t.value  # type: ignore
            )
            gains.sort(key=lambda t: t.value)  # type: ignore

            run = True
            current_spend_index = 0
            current_gain_index = 0
            while run:
                print("")
                s = spends[current_spend_index]
                g = gains[current_gain_index]

                print(f"si {current_spend_index} - gi {current_gain_index}")
                print(f"s {s.id} {s.value} - g {g.id} {g.value}")  # nopep8
                print("---")
                result = g.value + s.value

                g.value = result  # type: ignore
                s.value = result  # type: ignore

                if result > 0:
                    s.value = 0  # type: ignore
                elif result < 0:
                    g.value = 0  # type: ignore

                if s.value == 0:
                    current_spend_index = spends.index(s) + 1
                    if Adjustment.__is_last_index(s, spends):  # nopep8
                        run = False

                if g.value == 0:
                    current_gain_index = gains.index(g) + 1
                    if Adjustment.__is_last_index(g, gains):
                        run = False

                print(f"next si {current_spend_index} - next gi {current_gain_index}")  # nopep8
                print(f"s {s.id} {s.value} - g {g.id} {g.value}")  # nopep8
                print(f"run: {run}")
                print("")

            session.commit()
        except Exception as ex:
            session.rollback()
            raise ex

    @staticmethod
    def __normalize_and_validate(session: Session,
                                 transactions: list[Transaction] | list[int]) -> list[Transaction]:  # nopep8
        result: list[Transaction] = []

        if not Adjustment.__is_list_of_transactions(transactions):
            result = Adjustment.__to_transactions(
                session,
                transactions  # type: ignore
            )
        else:
            result = transactions  # type: ignore

        has_spend = False
        has_gain = False

        for t in result:
            if t.is_spend() and not has_spend:
                has_spend = True

            if t.is_gain() and not has_gain:
                has_gain = True

        if not has_spend or not has_gain:
            raise Exception(
                f"Transactions must have at least one spend and one gain"
            )

        return result

    @staticmethod
    def __is_last_index(obj: Transaction, list: list[Transaction]) -> bool:
        last_index = len(list) - 1
        return last_index == list.index(obj)

    @staticmethod
    def __to_transactions(session: Session,
                          ids: list[int]) -> list[Transaction]:
        result: list[Transaction] = []
        for id in ids:
            result.append(session.query(Transaction).get(id))

        return result

    @staticmethod
    def __is_list_of_transactions(list_param: list) -> bool:
        if len(list_param) == 0:
            return True

        if isinstance(list_param, list) and isinstance(list_param[0],
                                                       Transaction):
            return True

        return False
