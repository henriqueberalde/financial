from datetime import datetime
from typing import Any

from financial.entities.transaction import Transaction


def make_transaction(description: str = "transaction",
                     value: float = 1,
                     **fields: Any) -> Transaction:
    """Transaction of 01/10/2022 with balance 1, for user 1 / account 123."""
    return Transaction(**{
        "user_id": 1,
        "user_account": "123",
        "bank": "077",
        "date": datetime(2022, 10, 1),
        "description": description,
        "value": value,
        "balance": 1,
        **fields,
    })
