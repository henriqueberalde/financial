import calendar
import csv
import re

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from financial.importers.inter_credit_card import constants


@dataclass(frozen=True)
class InvoiceLine:
    date: datetime
    description: str
    category: str
    type: str
    value: Decimal


def invoice_month(path: Path) -> str:
    """Invoice month (YYYY-MM) taken from the file name."""
    match = re.match(constants.FILE_NAME_PATTERN, path.name)

    if match is None:
        raise ValueError(
            f"Invoice file name must be YYYY-MM.csv, got {path.name}")

    return f"{match.group(1)}-{match.group(2)}"


def read_invoice(path: Path) -> list[InvoiceLine]:
    """Purchases and refunds of an invoice file, without its payments."""
    with open(path, encoding=constants.CSV_ENCODING, newline="") as file:
        rows = list(csv.DictReader(file))

    return [_to_line(row) for row in rows
            if _normalize(row[constants.COLUMN_DESCRIPTION])
            not in constants.PAYMENT_LINES]


def parse_value(text: str) -> Decimal:
    """Invoice amount as a transaction value: purchases are negative."""
    amount = Decimal(re.sub(r"[^\d,]", "", text).replace(",", "."))
    return amount if text.strip().startswith("-") else -amount


def add_months(date: datetime, months: int) -> datetime:
    month_index = date.month - 1 + months
    year, month = date.year + month_index // 12, month_index % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return date.replace(year=year, month=month, day=day)


def _to_line(row: dict[str, str]) -> InvoiceLine:
    date = datetime.strptime(row[constants.COLUMN_DATE],
                             constants.CSV_DATE_FORMAT)
    description = _normalize(row[constants.COLUMN_DESCRIPTION])
    line_type = row[constants.COLUMN_TYPE]
    installment = re.match(constants.INSTALLMENT_PATTERN, line_type)

    if installment is not None:
        # Installments carry the purchase date; move them to their own month
        date = add_months(date, int(installment.group(1)) - 1)
        description = f"{description} - {line_type}"

    return InvoiceLine(date=date,
                       description=description,
                       category=row[constants.COLUMN_CATEGORY],
                       type=line_type,
                       value=parse_value(row[constants.COLUMN_VALUE]))


def _normalize(text: str) -> str:
    return " ".join(text.split())
