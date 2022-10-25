from distutils.cmd import Command
from distutils.dist import Distribution
import sys
import click

from click_repl import register_repl
from financial.inter_transactions_importer import InterTransactionsImporter
from financial.user import User


@click.group()
def cli():
    pass


@cli.command()
@click.option("-f", prompt="File path <example.csv>", help="csv file path")
@click.option("-i", prompt="User id <number>", help="user id")
@click.option("-a", prompt="User account <string>", help="user account number")
@click.option("-b", prompt="Bank <number>", help="bank number")
def inter_import_statement(f, i, a, b) -> None:
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


if __name__ == "__main__":
    register_repl(cli)
    cli()
