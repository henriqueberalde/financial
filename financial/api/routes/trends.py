from typing import Annotated

from fastapi import APIRouter, Query

from financial.api.dependencies import LedgerDep, MonthDep, PeriodDep
from financial.services.analytics import recurring, trends
from financial.services.analytics.constants import TOP_ITEMS

router = APIRouter(tags=["trends"])


@router.get("/recurring")
def read_recurring(frame: LedgerDep,
                   month: MonthDep) -> recurring.RecurringExpenses:
    """Recurring expenses of the trailing months ending at the month."""
    return recurring.recurring(frame, month)


@router.get("/category-variance")
def read_category_variance(frame: LedgerDep, month: MonthDep
                           ) -> list[trends.CategoryVariance]:
    return trends.category_variance(frame, month)


@router.get("/seasonality")
def read_seasonality(frame: LedgerDep) -> list[trends.SeasonalMonth]:
    return trends.seasonality(frame)


@router.get("/largest-expenses")
def read_largest_expenses(frame: LedgerDep,
                          period: PeriodDep,
                          limit: Annotated[int, Query(ge=1, le=100)] =
                          TOP_ITEMS) -> list[trends.LargeExpense]:
    return trends.largest(frame, *period, limit)
