from dataclasses import dataclass

from fastapi import APIRouter

from financial.api.dependencies import LedgerDep, MonthDep
from financial.services.analytics import ledger, overview

router = APIRouter(tags=["overview"])


@dataclass(frozen=True)
class Period:
    first_month: str | None
    last_month: str | None
    # Default month of the pages: the last one fully imported
    default_month: str | None


@router.get("/period")
def read_period(frame: LedgerDep) -> Period:
    """Months with transactions, to bound the period filters."""
    if frame.empty:
        return Period(None, None, None)

    months = ledger.months_with_data(frame)

    return Period(str(months[0]), str(months[-1]),
                  str(ledger.last_complete_month(frame)))


@router.get("/overview")
def read_overview(frame: LedgerDep, month: MonthDep) -> overview.Overview:
    return overview.overview(frame, month)
