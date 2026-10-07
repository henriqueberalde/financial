import click
import uvicorn
import financial.database as db

from pathlib import Path

from sqlalchemy.orm import Session
from click_repl import register_repl
from financial import settings
from financial.api.app import create_app
from financial.importers.inter.importer import TransactionsImporter
from financial.models.user import User
from financial.importers.inter import staging
from financial.importers.inter_credit_card import staging as card_staging
from financial.importers.inter_credit_card.constants import DATA_DIR
from financial.importers.inter_credit_card.importer import CreditCardImporter
from financial.models.category import Category
from financial.services import adjustments, categorization, transactions


@click.group()
def cli():
    pass


@cli.command()
@click.option("-f", prompt="File path <example.csv>", help="csv file path")
def inter_import_statement(f: str) -> None:
    """Financial Statement Import."""

    importer = TransactionsImporter(db.get_session())
    importer.import_from_csv(f)

    print('\ndone')


@cli.command()
@click.option("-user_id", prompt="User id", help="User id")
@click.option("-user_account", prompt="User account", help="User Account")
def merge_inter_transactions(user_id: int, user_account: str) -> None:
    """Merge inter_transactions into transactions to be categorized"""

    session = db.get_session()

    print('\nMerging inter transactions into transactions')
    staging.merge_into_transactions(session, User(user_id, user_account))

    reprocess_categories(session)

    print('\ndone')


@cli.command()
@click.option("-d", "directory", default=DATA_DIR, show_default=True,
              type=click.Path(exists=True, file_okay=False, path_type=Path),
              help="Folder with the invoices, one YYYY-MM.csv per month")
def inter_credit_card_import(directory: Path) -> None:
    """Stage Inter credit card invoices to be merged later."""

    importer = CreditCardImporter(db.get_session())
    files = importer.invoice_files(directory)

    if len(files) == 0:
        print(f'\nNo invoice files found in {directory}')

    for path in files:
        try:
            print(f'{path.name}: {importer.import_file(path)} lines staged')
        except ValueError as e:
            print(f'{path.name}: not imported. {e}')

    print('\ndone')


@cli.command()
@click.option("-user_id", prompt="User id", help="User id")
@click.option("-user_account", prompt="User account", help="User Account")
def inter_credit_card_merge(user_id: int, user_account: str) -> None:
    """Merge staged credit card invoices, deducting them from the card
    payments"""

    session = db.get_session()

    print('\nMerging credit card invoices into transactions')
    for result in card_staging.merge_into_transactions(
            session, User(user_id, user_account)):
        print_month_merge(result)

    reprocess_categories(session)

    print('\ndone')


@cli.command()
@click.option("-c", prompt="Context", help="transactions context")
@click.option("-ids", prompt="Ids of transactions", help="Ids of transactions")
def set_context(c: str, ids: str) -> None:
    """Set context of a list of transactions"""

    transactions.set_context(db.get_session(), ids, c)

    print('\ndone')


@cli.command()
@click.option("-name", prompt="Name", help="Category`s name")
@click.option("-sector", prompt="Sector", help="Category`s sector")
def create_category(name: str, sector: str) -> None:
    """Create a category with the name and sector"""

    session = db.get_session()
    session.add(Category(name=name, sector=sector))
    session.commit()

    print('\ndone')


@cli.command()
@click.option("-category_name", prompt="Category", help="Category`s name")
@click.option("-transaction_id",
              prompt="Transaction id",
              help="Transaction id")
def set_category(category_name: str, transaction_id: int) -> None:
    """Set transaction`s category manualy"""
    session = db.get_session()
    category = categorization.find_category(session, category_name)

    categorization.set_user_category(session, transaction_id,
                                     category.id)  # type: ignore

    print('\ndone')


@cli.command()
@click.option("-category_name", prompt="Category", help="Category`s name")
@click.option("-rule", prompt="Rule <regex>", help="Rule as regex")
def create_category_rule(category_name: str, rule: str) -> None:
    """Create a rule as a regex expression for categorize a transaction"""
    session = db.get_session()
    category = categorization.find_category(session, category_name)

    print('\nReprocessing categories')
    print_category_conflicts(
        categorization.add_rule(session, category.id, rule))  # type: ignore

    print('\ndone')


@cli.command()
@click.option("-reason", prompt="Reason", help="Reason of the adjustment")
@click.option("-transactions", prompt="Transactions Id", help="Id of all transactions to be ajusted")  # nopep8
def adjust(reason: str, transactions: str) -> None:
    """Adjust transactions to annul spends or gains"""
    session = db.get_session()
    ids_param: list[int] = []

    for id in transactions.split(" "):
        ids_param.append(int(id))  # type: ignore

    adjustments.add_adjustment(session, reason, ids_param)

    print('\ndone')


@cli.command()
def dashboard() -> None:
    """Serve the dashboard and its API"""
    uvicorn.run(create_app(), host=settings.dashboard_host(),
                port=settings.dashboard_port())


def reprocess_categories(session: Session) -> None:
    print('\nReprocessing categories')
    print_category_conflicts(categorization.reprocess_categories(session))


def print_month_merge(result: card_staging.MonthMerge) -> None:
    if result.error is not None:
        print(f'  {result.invoice_month}: not merged, kept staged. '
              f'{result.error}')
        return

    print(f'  {result.invoice_month}: {result.merged} transactions merged, '
          f'R$ {result.deducted:.2f} deducted from the card payment')


def print_category_conflicts(conflicts: list[str]) -> None:
    if len(conflicts) == 0:
        return

    print(f'\n{len(conflicts)} transactions skipped (category conflict):')
    for conflict in conflicts:
        print(f'  {conflict}')


def main() -> None:
    register_repl(cli)
    cli()


if __name__ == "__main__":
    main()
