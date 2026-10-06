from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Invoice CSV exported by Banco Inter, one file per invoice named YYYY-MM.csv
FILE_NAME_PATTERN = r"^(\d{4})-(\d{2})\.csv$"
CSV_ENCODING = "utf-8-sig"
CSV_DATE_FORMAT = "%d/%m/%Y"
COLUMN_DATE = "Data"
COLUMN_DESCRIPTION = "Lançamento"
COLUMN_CATEGORY = "Categoria"
COLUMN_TYPE = "Tipo"
COLUMN_VALUE = "Valor"
INSTALLMENT_PATTERN = r"^Parcela (\d+)/(\d+)$"

# Invoice lines mirroring checking account transactions, so not imported
PAYMENT_LINES = (
    "PAGTO DEBITO AUTOMATICO",
    "PAGAMENTO ON LINE",
    "DEVOLUCAO SDO CREDOR",
)

# Description of the checking account transactions that pay the invoice
PAYMENT_DESCRIPTION_PATTERN = r"fatura.*cart[aã]o inter"
