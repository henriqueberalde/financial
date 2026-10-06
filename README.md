An application to organize my financial life.

# Setup
Requirements:
- Python 3.14
- MySQL 8.4 (on Ubuntu: `sudo apt install mysql-server`; run the SQL commands below in `sudo mysql`)

### 1. Database
Create the application database and user. Choose a password and use it in `.env` (step 3):

```sql
CREATE DATABASE financial;
CREATE USER 'financial'@'localhost' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON financial.* TO 'financial'@'localhost';
```

### 2. Virtual environment
From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"          # installs the `financial` package in editable mode with dev tools
```

To leave the virtual environment: `deactivate`. Next time, just run `source .venv/bin/activate`.

### 3. Configuration (.env)
Passwords and per-environment values live in `.env`, which is not versioned:

```bash
cp .env_example .env             # then set the database password in .env
```

| Variable | Usage |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL of the application database (CLI, notebooks and Alembic) |

Variables set in the environment take precedence over `.env`.
Library settings and business rules live in the `constants.py` of the package they belong to (e.g. the Inter CSV layout and bank code in `financial/importers/inter/constants.py`).

### 4. Migrations
Alembic uses `DATABASE_URL` from `.env`:

```bash
alembic upgrade head
```

To migrate another database, override the variable:

```bash
DATABASE_URL=<url> alembic upgrade head
```

# Usage
With the virtual environment activated:

### CLI
```bash
financial --help                 # lists the commands
financial repl                   # interactive mode
```

Basic flow to import a Banco Inter statement (`;`-separated CSV, saved in `data/`):

```bash
financial inter-import-statement -f data/statement.csv
financial merge-inter-transactions -user_id 1 -user_account <account>
```

### Jupyter Notebook
Exploratory analyses live in `notebooks/`. With the virtual environment activated:

```bash
jupyter notebook notebooks/analise_financeira.ipynb
```

Notebook outputs contain real financial data. To keep them out of commits, enable `nbstripout` once per clone (it strips outputs on `git add` without changing the local file):

```bash
nbstripout --install
```

# Tests
Tests use an in-memory SQLite database, created from the models for every test. MySQL is not needed:

```bash
pytest                           # tests + coverage report
pytest --cov-report=html         # browsable report in htmlcov/index.html
pycodestyle financial tests      # lint
```

Coverage (lines and branches) is measured with `pytest-cov`, and `pytest` fails below 95% (`pyproject.toml`).
To build sample transactions in tests, use `make_transaction` from `tests/factories.py`.

# TODO
* [ ] Use https://www.mage.ai/
* [x] Add bank column
* [x] Receive file_path, user_id, user_account and bank as input
* [x] Log messages
* [x] Try catch
* [x] Separate data NORMALIZATION from LOAD and PERSISTENCE
* [x] Organize classes and methods
* [x] Import Inters Full history
* [x] Automated tests
* [x] Lint
* [x] Github
* [x] `bonus` REPL
* [x] Add categorization of transaction
* [x] Add encapsulation `isolate spending by user context`
* [x] Add category rules `automatic set category`
* [x] Update unit tests not dependent from db
* [x] Update unit tests dependent from db
* [x] Split import table from transactions table
* [x] Make import command cleanup the table after execution
* [x] Import part statement `avoid duplication using the date`
* [x] Reprocess categorization transactions
* [x] Run reprocess categorization after create or update category or category_rule
* [x] Add categorization per transaction `in separated table because of the reprocessment of categorization`
* [x] Annul some spend(s) based on gain(s)
* [x] Create groups of categories (Like essesials and etc)
* [ ] Remove Outros Category
* [ ] Avoid category duplication
* [ ] Add priority on category to sort by it
* [ ] ~~Remove "set X of many" feature~~

# Visualization
* [x] Statement report by date `begin and end`
* [x] Grouped statement report by date `begin and end`
* [x] Grouped graph report `many months`
* [x] See every month in the same table
* [x] Align numbers at right
* [ ] Money format
* [ ] `all month` Hover on one month in all months` table to show percentage of diference between last value
* [ ] `all month` Select a category and shows it on graph comparing all months and other things
* [ ] `all month` Add total in every month
* [ ] Set filters on url

# Answer theese questions with features
* [x] How much did I spent `filter month`?
* [x] How much did I spent per sector (essensial and etc) `filter month`?
* [x] How much did I spent per category `filter month`?
* [x] How much did I took off from investment `filter month`?

# Technical things
* [x] Separate file load from data_frame manipulation
* [ ] On creating category rule select category by name case insensitivity
* [ ] DocString
* [ ] Use python Decimal in everything to avoid rounding errors
* [ ] Set some tests to use decimal values
* [ ] Add Prettier
* [ ] ~~Use IMDB (in-memory database) for unit tests~~

# Priority
* [ ] Add grouped context spends on dashboard
* [ ] Import Nubank
* [ ] Feature of transaction substitution
