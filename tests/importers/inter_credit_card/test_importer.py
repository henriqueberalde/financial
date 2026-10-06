import shutil

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from financial.importers.inter_credit_card.importer import CreditCardImporter
from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction

INVOICES = Path("tests/data/inter_credit_card")


def test_invoice_files_lists_csv_files_in_order(tmp_path: Path):
    for name in ["2024-07.csv", "2024-06.csv", "notes.txt"]:
        (tmp_path / name).touch()

    assert [p.name for p in CreditCardImporter.invoice_files(tmp_path)] == \
        ["2024-06.csv", "2024-07.csv"]


def test_import_file_stages_lines_with_invoice_month(session: Session):
    staged = CreditCardImporter(session).import_file(INVOICES / "2024-06.csv")

    rows = session.query(InterCreditCardTransaction).all()
    assert staged == len(rows) == 5
    assert {row.invoice_month for row in rows} == {"2024-06"}
    assert rows[0].description == "MERCADO EXEMPLO SAO PAULO BRA"
    assert rows[0].category == "SUPERMERCADO"


def test_import_file_gives_identical_lines_distinct_hashes(session: Session):
    CreditCardImporter(session).import_file(INVOICES / "2024-06.csv")

    iof = session.query(InterCreditCardTransaction) \
        .filter_by(description="IOF INTERNACIONAL").all()
    assert len(iof) == 2
    assert iof[0].hash != iof[1].hash


def test_import_file_replaces_the_month_and_keeps_others(session: Session):
    importer = CreditCardImporter(session)
    importer.import_file(INVOICES / "2024-07.csv")
    importer.import_file(INVOICES / "2024-06.csv")
    hashes = {row.hash for row in session.query(InterCreditCardTransaction)}

    importer.import_file(INVOICES / "2024-06.csv")

    assert session.query(InterCreditCardTransaction).count() == 6
    assert {row.hash for row in session.query(InterCreditCardTransaction)} \
        == hashes


def test_import_file_rejects_files_not_named_by_month(session: Session,
                                                      tmp_path: Path):
    path = tmp_path / "fatura-inter-2024-06.csv"
    shutil.copy(INVOICES / "2024-06.csv", path)

    with pytest.raises(ValueError):
        CreditCardImporter(session).import_file(path)

    assert session.query(InterCreditCardTransaction).count() == 0
