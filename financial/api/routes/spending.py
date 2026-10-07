from typing import Annotated

from fastapi import APIRouter, Depends, Query

from financial.api.dependencies import LedgerDep, PeriodDep
from financial.services.analytics import spending
from financial.services.analytics.constants import PAGE_SIZE, TOP_ITEMS
from financial.services.analytics.ledger import Source
from financial.services.analytics.spending import SpendingFilter

router = APIRouter(tags=["spending"])


def spending_filter(period: PeriodDep,
                    sector: str | None = None,
                    category: str | None = None,
                    merchant: str | None = None,
                    source: Source | None = None
                    ) -> SpendingFilter:
    return SpendingFilter(*period, sector, category, merchant, source)


FilterDep = Annotated[SpendingFilter, Depends(spending_filter)]


@router.get("/spending/tree")
def read_tree(frame: LedgerDep,
              spending_filter: FilterDep) -> list[spending.TreeNode]:
    """Expenses as sector > category > merchant."""
    return spending.tree(frame, spending_filter)


@router.get("/spending/timeline")
def read_timeline(frame: LedgerDep,
                  spending_filter: FilterDep,
                  granularity: spending.Granularity = "month"
                  ) -> spending.Timeline:
    return spending.timeline(frame, spending_filter, granularity)


@router.get("/spending/merchants")
def read_merchants(frame: LedgerDep,
                   spending_filter: FilterDep,
                   limit: Annotated[int, Query(ge=1, le=100)] = TOP_ITEMS
                   ) -> list[spending.MerchantTotal]:
    return spending.merchants(frame, spending_filter, limit)


@router.get("/transactions")
def read_transactions(frame: LedgerDep,
                      spending_filter: FilterDep,
                      search: str | None = None,
                      limit: Annotated[int, Query(ge=1, le=500)] = PAGE_SIZE,
                      offset: Annotated[int, Query(ge=0)] = 0
                      ) -> spending.TransactionPage:
    """Routine expenses of the filter, newest first."""
    return spending.transactions(frame, spending_filter, search, limit,
                                 offset)
