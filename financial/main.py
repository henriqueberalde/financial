import click
import financial.entities.db as db

from sqlalchemy import delete
from click_repl import register_repl
from financial.inter.transactions_importer import TransactionsImporter
from financial.entities.user import User
from financial.entities.transaction import Transaction
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule

session = db.get_session()


@click.group()
def cli():
    pass


@cli.command()
@click.option("-f", prompt="File path <example.csv>", help="csv file path")
@click.option("-i", prompt="User id <number>", help="user id")
@click.option("-a", prompt="User account <string>", help="user account number")
@click.option("-b", prompt="Bank <number>", help="bank number")
def inter_import_statement(f: str, i: int, a: str, b: str) -> None:
    """Financial Statement Import."""

    file_path = f
    user_id = i
    user_account = a
    bank = b
    print('\nData')
    print(f'user_id:{user_id}')
    print(f'user_account:{user_account}')
    print(f'bank:{bank}')

    importer = TransactionsImporter(session, User(user_id, user_account))
    importer.import_from_csv(file_path)

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
def create_category(name: str) -> None:
    """Create a category with the name"""

    session.add(Category(name=name))
    session.commit()

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

    print('\ndone')


@cli.command()
def cleanup() -> None:
    """Clean up transactions table on db"""
    session = db.get_session()
    session.execute(delete(Transaction))
    session.commit()

    print('\ndone')


if __name__ == "__main__":
    register_repl(cli)
    cli()
