import hashlib

from datetime import datetime
from typing import Any

HASH_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def transaction_hash(date: datetime,
                     description: Any,
                     value: Any,
                     balance: Any) -> str:
    formatted_date = date.strftime(HASH_DATE_FORMAT)
    return sha256(f"{formatted_date}{description}{value}{balance}")
