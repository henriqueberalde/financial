An application to organize my financial life.

# Setup
Requisitos:
- Python 3.14
- MySQL 8.4 (no Ubuntu: `sudo apt install mysql-server`; os comandos SQL abaixo rodam em `sudo mysql`)

### 1. Banco de dados
Crie o banco e o usuário da aplicação. Escolha uma senha e use-a no `.env` (passo 3):

```sql
CREATE DATABASE financial;
CREATE USER 'financial'@'localhost' IDENTIFIED BY '<senha>';
GRANT ALL PRIVILEGES ON financial.* TO 'financial'@'localhost';

-- usado apenas pelos testes
CREATE DATABASE financial_test;
CREATE USER 'financial_test'@'localhost' IDENTIFIED BY 'pass123';
GRANT ALL PRIVILEGES ON financial_test.* TO 'financial_test'@'localhost';
```

### 2. Ambiente virtual
Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .                 # instala o pacote `financial` em modo editável
```

Para sair do ambiente virtual: `deactivate`. Nas próximas vezes basta rodar `source .venv/bin/activate`.

### 3. Configuração (.env)
Senhas e valores que mudam por ambiente ficam no `.env`, que não é versionado:

```bash
cp .env_example .env             # depois edite o .env com a senha do banco
```

| Variável | Uso |
|---|---|
| `DATABASE_URL` | URL do SQLAlchemy do banco da aplicação (app, CLI, dashboard, notebooks e Alembic) |
| `DASHBOARD_HOST`, `DASHBOARD_PORT` | Endereço do dashboard (padrão `127.0.0.1:8050`) |
| `DASHBOARD_DEBUG` | `true` ativa o modo debug do Dash (padrão `false`) |

Variáveis definidas no ambiente têm prioridade sobre o `.env`.
Constantes de bibliotecas e regras de negócio (formato do CSV do Inter, código do banco etc.) ficam em `financial/constants.py`.

### 4. Migrations
O Alembic usa o `DATABASE_URL` do `.env`:

```bash
alembic upgrade head
```

Para aplicar em outro banco (por exemplo, o de testes), sobrescreva a variável:

```bash
DATABASE_URL=mysql+pymysql://financial_test:pass123@localhost/financial_test alembic upgrade head
```

# Usage
Com o ambiente virtual ativado:

### CLI
```bash
python financial/cli.py --help   # lista os comandos
python financial/cli.py repl     # modo interativo
```

Fluxo básico de importação de um extrato do Inter (CSV separado por `;`, salvo em `assets/`):

```bash
python financial/cli.py inter-import-statement -f assets/extrato.csv
python financial/cli.py merge-inter-transactions -user_id 1 -user_account <conta>
```

### Dash Board
```bash
python financial/dash_board/app.py
```
Acesse http://127.0.0.1:8050

### Jupyter Notebook
Análises exploratórias ficam em `notebooks/`. Com o ambiente virtual ativado:

```bash
jupyter notebook notebooks/analise_financeira.ipynb
```

As saídas dos notebooks contêm dados financeiros reais. Para não commitá-las, ative o `nbstripout` uma vez por clone (ele limpa as saídas no `git add`, sem alterar o arquivo local):

```bash
nbstripout --install
```

# Tests
Requer o banco `financial_test` com as migrations aplicadas:

```bash
pytest
pycodestyle financial tests      # lint
```

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
* [ ] Use dash pages

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
* [ ] Turn poc dashoboard into a feature with tests and etc
* [ ] Add grouped context spends on dashboard
* [ ] Import Nubank
* [ ] Feature of transaction substitution
