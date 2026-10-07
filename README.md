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
| `DASHBOARD_HOST`, `DASHBOARD_PORT` | Address of the dashboard (default `127.0.0.1:8000`) |

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

### Inter credit card invoices
Export each invoice from the Inter app as CSV and save it as `YYYY-MM.csv` (the month the invoice is paid) in `financial/importers/inter_credit_card/data/`. Then:

```bash
financial inter-credit-card-import    # stages the invoices (-d <folder> to read another folder)
financial inter-credit-card-merge -user_id 1 -user_account <account>
```

The merge runs one invoice month at a time:
- the invoice purchases and refunds become transactions (payment lines of the invoice are skipped, they are already in the statement);
- their total is deducted from the `value` of the checking account transaction that paid the card in that month (or what is left of an advance payment made in the previous month); `original_value` is kept;
- installments are dated in the month they are charged and get ` - Parcela N/M` in the description;
- a month whose payment is not found is not merged and stays staged, so it can be merged again after the statement with the payment is imported.

Card purchases have no `balance`, since they do not change the checking account balance.

### Dashboard
```bash
financial dashboard              # then open http://127.0.0.1:8000
```

The pages answer one question each. Filters live in the URL, so any view can be bookmarked:

| Page | What it shows |
|---|---|
| Visão geral | Income, expense, result and savings rate of the month against the average of the 12 months before; monthly flow; account balance; expenses per sector; alerts (categories above average, new recurring expenses, price increases, uncategorized share above the target) |
| Gastos | Drill-down of the expenses: sector > category > merchant (treemap) and year > month > day (timeline); top merchants; the transactions, whose category can be changed in place |
| Recorrentes e anomalias | Merchants charged in most of the last 12 months, flagged as new or with a price increase; this month against the average per category; seasonality; largest expenses |
| Dados | Categorization quality: uncategorized share per year and against the 5% target, how expenses got their category (rule, manual or none), the uncategorized merchants that weigh the most (with a button to create a rule), rule conflicts and rules that match nothing |

Conventions shared with the notebook: investments (applications, redemptions and Tesouro Direto) are neither income nor expense; transactions with a `context` (trips and projects) are left out; `value` is used, so adjustments count. Pages open on the last complete month. The thresholds are in `financial/services/analytics/constants.py`.

The API behind the pages is documented at `http://127.0.0.1:8000/docs`. The pages are plain JavaScript modules in `financial/web/`, with no build step; ECharts and the fonts load from CDNs.

### Jupyter Notebook
Exploratory analyses live in `notebooks/`. With the virtual environment activated:

```bash
jupyter notebook notebooks/analise_financeira.ipynb
```

Notebook outputs contain real financial data. To keep them out of commits, enable `nbstripout` once per clone (it strips outputs on `git add` without changing the local file):

```bash
nbstripout --install
```

# Project structure
| Path | Contents |
|---|---|
| `financial/cli.py` | `financial` command (CLI and REPL) |
| `financial/models/` | SQLAlchemy tables |
| `financial/services/` | Business operations: categorization, adjustments, transaction contexts |
| `financial/services/analytics/` | Dashboard aggregations over the transactions ledger |
| `financial/api/` | REST API of the dashboard (FastAPI), one router per subject |
| `financial/web/` | Dashboard pages (HTML, CSS and JavaScript modules) |
| `financial/importers/staging.py` | Insert of staged rows into transactions, shared by the importers |
| `financial/importers/inter/` | Banco Inter statement import: parsing, staging table, merge and constants |
| `financial/importers/inter_credit_card/` | Banco Inter credit card invoices: parsing, staging table, month-by-month merge; invoices go in its `data/` folder (not versioned) |
| `financial/settings.py`, `financial/database.py` | `.env` settings and database session |
| `alembic/` | Database migrations |
| `notebooks/` | Exploratory analyses |
| `data/` | Personal statements and dumps (not versioned) |
| `tests/` | Unit tests, mirroring `financial/`; fixtures in `tests/data/` |

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
* [x] Money format
* [ ] `all month` Hover on one month in all months` table to show percentage of diference between last value
* [ ] `all month` Select a category and shows it on graph comparing all months and other things
* [ ] `all month` Add total in every month
* [x] Set filters on url

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
