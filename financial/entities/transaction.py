import hashlib
import re
import financial.entities.db as db

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Table  # nopep8
from sqlalchemy.orm import relationship
from typing import Iterable, Any
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.normalization_error import NormalizationError
from financial.entities.category_rule_conflict_error import CategoryRuleConflictError  # nopep8


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

    @staticmethod
    def set_categories_by_rules(session: Session,
                                category_rules: list[CategoryRule]) -> None:
        errors: list[str] = []

        transactions = session.query(Transaction).all()

        for transaction in transactions:
            try:
                category_id = Transaction.__fetch_category_id(
                    transaction.description,
                    category_rules)

                if category_id is not None:
                    session.add(transaction)
                    transaction.category_id = category_id
            except CategoryRuleConflictError as e:
                errors.append(e.message)

        if (len(errors) > 0):
            raise NormalizationError(errors)

        session.commit()

    @staticmethod
    def __fetch_category_id(description: str,
                            category_rules: list[CategoryRule]) -> str | None:
        matched_rules: list[CategoryRule] = []

        for rule in category_rules:
            if re.search(str(rule.rule),
                         description,
                         re.IGNORECASE) is not None:
                matched_rules.append(rule)

        distinct_matched_categories = CategoryRule.distinct_categories(
            matched_rules
        )

        if len(distinct_matched_categories) == 0:
            return None

        if len(distinct_matched_categories) == 1:
            return str(matched_rules[0].category.id)

        raise CategoryRuleConflictError(description, matched_rules)

    def __generate_hash(self) -> None:
        date = self.date.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
        concat_result = f"{date}{self.description}{self.value}{self.balance}"  # nopep8
        self.original_hash = Transaction.str_to_hash(concat_result)

    @staticmethod
    def str_to_hash(str: str) -> str:
        return hashlib.sha256(str.encode('utf-8')).hexdigest()
