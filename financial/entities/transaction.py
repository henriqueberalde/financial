import financial.entities.db as db
import re

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from typing import Iterable, Any
from financial.entities.category_rule import CategoryRule
from financial.entities.normalization_error import NormalizationError
from financial.entities.transactions_categories import TransactionsCategories
from financial.entities.category_rule_conflict_error import CategoryRuleConflictError  # nopep8


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

    def is_spend(self) -> bool:
        return bool(self.transaction.value < 0)

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
    def set_categories_by_user(session: Session) -> None:
        try:
            TransactionsCategories.set_transactions_categories(session)
        except Exception as e:
            print(f"Error while setting specific categorization. {e}")

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
