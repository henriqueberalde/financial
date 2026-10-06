import click
import financial.database as db

from sqlalchemy.orm import Session
from click_repl import register_repl
from financial.inter.transactions_importer import TransactionsImporter
from financial.models.user import User
from financial.models.transaction import Transaction
from financial.models.inter_transaction import InterTransaction
from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.transaction_category import TransactionCategory
from financial.models.adjustment import Adjustment


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
    InterTransaction.merge_to_transactions(session,
                                           User(user_id, user_account))

    reprocess_categories(session)

    print('\ndone')


@cli.command()
@click.option("-c", prompt="Context", help="transactions context")
@click.option("-ids", prompt="Ids of transactions", help="Ids of transactions")
def set_context(c: str, ids: str) -> None:
    """Set context of a list of transactions"""

    Transaction.set_context_of_many(db.get_session(), ids, c)

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
    category = find_category(session, category_name)

    tc = TransactionCategory(category_id=category.id,
                             transaction_id=transaction_id)
    session.add(tc)
    session.commit()
    TransactionCategory.set_categories_by_user(session)

    print('\ndone')


@cli.command()
@click.option("-category_name", prompt="Category", help="Category`s name")
@click.option("-rule", prompt="Rule <regex>", help="Rule as regex")
def create_category_rule(category_name: str, rule: str) -> None:
    """Create a rule as a regex expression for categorize a transaction"""
    session = db.get_session()
    category = find_category(session, category_name)

    session.add(CategoryRule(category_id=category.id, rule=rule))
    session.commit()

    reprocess_categories(session)

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

    Adjustment.add(session, reason, ids_param)

    print('\ndone')


def find_category(session: Session, name: str) -> Category:
    return session.query(Category).filter_by(name=name).one()


def reprocess_categories(session: Session) -> None:
    print('\nReprocessing categories')
    conflicts = Transaction.set_categories_by_rules(
        session, session.query(CategoryRule).all())
    print_category_conflicts(conflicts)

    TransactionCategory.set_categories_by_user(session)


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
