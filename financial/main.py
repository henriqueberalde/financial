import click
import financial.db as db

from distutils.cmd import Command
from distutils.dist import Distribution
from click_repl import register_repl
from financial.inter_transactions_importer import InterTransactionsImporter
from financial.user import User
from financial.transaction import Transaction
from financial.category import Category
from financial.category_rule import CategoryRule


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

    importer = InterTransactionsImporter(User(user_id, user_account))
    importer.import_from_csv(file_path)

    print('\ndone')


@cli.command()
@click.option("-c", prompt="Category", help="transactions category")
@click.option("-ids", prompt="Ids of transactions", help="Ids of transactions")
def set_category(c: str, ids: str) -> None:
    """Set category of a list of transactions"""

    Transaction.set_category_of_many(ids, c)

    print('\ndone')


@cli.command()
@click.option("-c", prompt="Context", help="transactions context")
@click.option("-ids", prompt="Ids of transactions", help="Ids of transactions")
def set_context(c: str, ids: str) -> None:
    """Set context of a list of transactions"""

    Transaction.set_context_of_many(ids, c)

    print('\ndone')


@cli.command()
@click.option("-name", prompt="Name", help="Category`s name")
def create_category(name: str) -> None:
    """Create a category with the name"""

    Category(name=name).save()

    print('\ndone')


@cli.command()
@click.option("-category_name", prompt="Category", help="Category`s name")
@click.option("-rule", prompt="Rule <regex>", help="Rule as regex")
def create_category_rule(category_name: str, rule: str) -> None:
    """Create a rule as a regex expression for categorize a transaction"""
    session = db.get_session()
    category = session.query(Category).filter_by(name=category_name).one()

    CategoryRule(category_id=category.id, rule=rule).save()

    print('\ndone')


if __name__ == "__main__":
    register_repl(cli)
    cli()
