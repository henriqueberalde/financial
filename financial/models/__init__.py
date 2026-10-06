"""SQLAlchemy models.

Importing this package registers every table in financial.database.Base,
which the string-based relationship() lookups depend on.
"""
from financial.models.adjustment import Adjustment
from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.transaction import Transaction
from financial.models.transaction_category import TransactionCategory

__all__ = [
    "Adjustment",
    "Category",
    "CategoryRule",
    "Transaction",
    "TransactionCategory",
]
