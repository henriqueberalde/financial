import re

from sqlalchemy.orm import Session

from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.transaction import Transaction
from financial.models.transaction_category import TransactionCategory


class CategoryRuleConflictError(Exception):
    def __init__(self,
                 description: str,
                 conflicted_rules: list[CategoryRule]):
        categories = distinct_category_names(conflicted_rules)
        self.message = f"More than one category match. Description: '{description}', Matches: {categories}"  # nopep8
        self.conflicted_category_rules = conflicted_rules
        super().__init__(self.message)


def distinct_category_names(rules: list[CategoryRule]) -> list[str]:
    names: list[str] = []

    for rule in rules:
        if rule.category.name not in names:
            names.append(rule.category.name)

    return names


def find_category(session: Session, name: str) -> Category:
    return session.query(Category).filter_by(name=name).one()


def set_user_category(session: Session,
                      transaction_id: int,
                      category_id: int) -> None:
    """Pin the category chosen by the user to a transaction, replacing a
    previous choice. User choices win over category rules."""
    session.query(TransactionCategory).filter_by(
        transaction_id=transaction_id).delete()
    session.add(TransactionCategory(category_id=category_id,
                                    transaction_id=transaction_id))
    session.commit()
    set_categories_by_user(session)


def add_rule(session: Session, category_id: int, rule: str) -> list[str]:
    """Create a regex rule for a category and reprocess every transaction.
    Returns the conflict messages of the transactions that were skipped."""
    try:
        re.compile(rule)
    except re.error as e:
        raise ValueError(f"Invalid rule '{rule}': {e}") from e

    session.add(CategoryRule(category_id=category_id, rule=rule))
    session.commit()

    return reprocess_categories(session)


def reprocess_categories(session: Session) -> list[str]:
    """Apply category rules, then the categories set by the user.
    Returns the conflict messages of the transactions that were skipped."""
    conflicts = set_categories_by_rules(session,
                                        session.query(CategoryRule).all())
    set_categories_by_user(session)

    return conflicts


def set_categories_by_rules(session: Session,
                            category_rules: list[CategoryRule]) -> list[str]:
    """Set categories by rules, skipping transactions matched by rules
    of more than one category. Returns the conflict messages."""
    errors: list[str] = []

    for transaction in session.query(Transaction).all():
        try:
            category_id = category_id_for(str(transaction.description),
                                          category_rules)

            if category_id is not None:
                transaction.category_id = category_id  # type: ignore
        except CategoryRuleConflictError as e:
            errors.append(e.message)

    session.commit()

    return errors


def category_id_for(description: str,
                    category_rules: list[CategoryRule]) -> str | None:
    matched_rules = [
        rule for rule in category_rules
        if re.search(str(rule.rule), description, re.IGNORECASE) is not None
    ]
    matched_categories = distinct_category_names(matched_rules)

    if len(matched_categories) == 0:
        return None

    if len(matched_categories) == 1:
        return str(matched_rules[0].category.id)

    raise CategoryRuleConflictError(description, matched_rules)


def set_transactions_categories(session: Session) -> None:
    for transaction_category in session.query(TransactionCategory).all():
        transaction_category.transaction.category_id = \
            transaction_category.category_id

    session.commit()


def set_categories_by_user(session: Session) -> None:
    try:
        set_transactions_categories(session)
    except Exception as e:
        print(f"Error while setting specific categorization. {e}")
