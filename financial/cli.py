import click
import financial.entities.db as db

from sqlalchemy import delete
from sqlalchemy.orm import Session
from click_repl import register_repl
from financial.inter.transactions_importer import TransactionsImporter
from financial.entities.user import User
from financial.entities.transaction import Transaction
from financial.entities.inter_transaction import InterTransaction
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.transactions_categories import TransactionsCategories
from financial.entities.adjustement import Adjustment


session: Session = db.get_session()


@click.group()
def cli():
    pass


@cli.command()
@click.option("-f", prompt="File path <example.csv>", help="csv file path")
def inter_import_statement(f: str) -> None:
    """Financial Statement Import."""

    file_path = f

    importer = TransactionsImporter(session)
    importer.import_from_csv(file_path)

    print('\ndone')


@cli.command()
@click.option("-user_id", prompt="User id", help="User id")
@click.option("-user_account", prompt="User account", help="User Account")
def merge_inter_transactions(user_id: int, user_account: str) -> None:
    """Merge inter_transactions into transactions to be categorized"""

    print('\nMerging inter transactions into transactions')
    InterTransaction.merge_to_transactions(session,
                                           User(user_id, user_account))

    print('\nReprocessing Categorization')
    Transaction.set_categories_by_rules(session,
                                        session.query(CategoryRule).all())

    TransactionsCategories.set_categories_by_user(session)

    print('\ndone')


@cli.command()
@click.option("-c", prompt="Context", help="transactions context")
@click.option("-ids", prompt="Ids of transactions", help="Ids of transactions")
def set_context(c: str, ids: str) -> None:
    """Set context of a list of transactions"""

    Transaction.set_context_of_many(session, ids, c)

    print('\ndone')


@cli.command()
@click.option("-name", prompt="Name", help="Category`s name")
@click.option("-sector", prompt="Sector", help="Category`s sector")
def create_category(name: str, sector: str) -> None:
    """Create a category with the name and sector"""

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
    category = session.query(Category).filter_by(name=category_name).one()

    tc = TransactionsCategories(category_id=category.id,
                                transaction_id=transaction_id)
    session.add(tc)
    session.commit()
    TransactionsCategories.set_categories_by_user(session)

    print('\ndone')


@cli.command()
@click.option("-category_name", prompt="Category", help="Category`s name")
@click.option("-rule", prompt="Rule <regex>", help="Rule as regex")
def create_category_rule(category_name: str, rule: str) -> None:
    """Create a rule as a regex expression for categorize a transaction"""
    session = db.get_session()
    category = session.query(Category).filter_by(name=category_name).one()

    session.add(CategoryRule(category_id=category.id, rule=rule))
    session.commit()

    print('\nReprocessing categories')
    Transaction.set_categories_by_rules(session,
                                        session.query(CategoryRule).all())
    TransactionsCategories.set_categories_by_user(session)

    print('\ndone')


@cli.command()
@click.option("-reason", prompt="Reason", help="Reason of the adjustment")
@click.option("-transactions", prompt="Transactions Id", help="Id of all transactions to be ajusted")  # nopep8
def adjust(reason: str, transactions: str) -> None:
    """Adjust transactions to annul spends or gains"""
    session = db.get_session()
    ids_param: list[int] = []

    for id in transactions.split(" "):
        ids_param.append(int(id))

    Adjustment.add(session, reason, ids_param)

    print('\ndone')


if __name__ == "__main__":
    register_repl(cli)
    cli()
