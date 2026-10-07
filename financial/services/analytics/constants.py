# Descriptions of transactions that move money into or out of investments.
# They change the net worth composition, so they are neither income nor
# expense.
INVESTMENT_PATTERN = (
    r"^(?:aplica[cç][aã]o|resgate)\b|tesouro direto|^debito online td\b"
)

# Name given to transactions without category or sector
UNCATEGORIZED = "Sem categoria"

# Months used as reference for averages and recurring expenses
TRAILING_MONTHS = 12

# A merchant is recurring when it shows up in at least this many months
RECURRING_MIN_MONTHS = 6

# A merchant is a new recurring one when it shows up in each of the last
# months below, and in none of the trailing months before them
NEW_RECURRING_MONTHS = 3

# A recurring expense with a stable value whose last month is this much
# above its usual value had a price increase
STABLE_VALUE_MAX_VARIATION = 0.15
PRICE_INCREASE_MIN_RATIO = 0.05

# A category is above average when it exceeds the trailing average by both
ABOVE_AVERAGE_MIN_RATIO = 0.25
ABOVE_AVERAGE_MIN_VALUE = 100.0

# Share of the expenses without category considered acceptable
UNCATEGORIZED_TARGET = 0.05

# Merchants shown per category in the spending tree; the rest are summed up
TREE_MERCHANTS_PER_CATEGORY = 10

# Default size of rankings and pages
TOP_ITEMS = 15
PAGE_SIZE = 50
