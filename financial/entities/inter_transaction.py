import hashlib
import financial.entities.db as db

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from financial.entities.user import User


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
                                    balance,
                                    original_hash
                                )
                                SELECT
                                    :user_id,
                                    :user_account,
                                    :bank,
                                    it.date,
                                    it.description,
                                    it.value,
                                    it.value,
                                    it.balance,
                                    it.hash
                                from inter_transactions it
                                left join transactions t on
                                    it.hash = t.original_hash
                            where t.id is null;""", {
                                "user_id": user.id,
                                "user_account": user.account,
                                "bank": "077",
                            })
            session.commit()

        except Exception as e:
            print(f"Error while merging transactions from inter.{e}")
            session.rollback()

    def __generate_hash(self) -> None:
        date = self.date.strftime("%Y-%m-%d %H:%M:%S")
        concat_result = f"{date}{self.description}{self.value}{self.balance}"  # nopep8
        self.hash = InterTransaction.str_to_hash(concat_result)

    @staticmethod
    def str_to_hash(str: str) -> str:
        return hashlib.sha256(str.encode('utf-8')).hexdigest()
