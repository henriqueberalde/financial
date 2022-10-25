import sys

from financial.inter_transactions_importer import InterTransactionsImporter
from financial.user import User

if (len(sys.argv) < 4):
    print("Invalid parameters. " +
          "command <csv_file_path> <user_id> <user_account> <bank>")
    sys.exit(1)

file_path = sys.argv[1]
user_id = sys.argv[2]
user_account = sys.argv[3]
bank = sys.argv[4]
print('\nData')
print(f'user_id:{user_id}')
print(f'user_account:{user_account}')
print(f'bank:{bank}')

importer = InterTransactionsImporter(User(user_id, user_account))
importer.import_from_csv(file_path)

print('\ndone')
