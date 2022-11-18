import financial.entities.db as db
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from financial.entities.user import User


class InterTransaction(db.Base):
    __tablename__ = "inter_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    description = Column(String)
    value = Column(Numeric)
    balance = Column(Numeric)

    @staticmethod
    def cleanup_inter_transactions(session: Session) -> None:
        session.execute("DELETE FROM inter_transactions;")
        session.execute("ALTER TABLE inter_transactions AUTO_INCREMENT = 1;")

    @staticmethod
    def merge_to_transactions(session: Session, user: User) -> None:
        try:
            session.execute("""INSERT INTO transactions (
                                    user_id,
                                    user_account,
                                    bank,
                                    date,
                                    description,
                                    value,
                                    original_value,
                                    balance
                                )
                                SELECT
                                    :user_id,
                                    :user_account,
                                    :bank,
                                    it.date,
                                    it.description,
                                    it.value,
                                    it.value,
                                    it.balance
                                from inter_transactions it
                                left join transactions t on
                                    it.date = t.date and
                                    it.description = t.description and
                                    it.value = t.value and
                                    it.balance = t.balance
                            where t.id is null;""", {
                                "user_id": user.id,
                                "user_account": user.account,
                                "bank": "077",
                            })
            session.commit()

        except Exception as e:
            print(f"Error while merging transactions from inter.{e}")
            session.rollback()
