from collections.abc import Iterator
from functools import cache
from typing import Annotated

import pandas as pd

from fastapi import Depends, HTTPException, Query
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

import financial.database as db

from financial.services.analytics import ledger
from financial.services.analytics.constants import TRAILING_MONTHS

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@cache
def engine() -> Engine:
    return db.get_engine()


def get_session() -> Iterator[Session]:
    with Session(engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_ledger(session: SessionDep) -> pd.DataFrame:
    return ledger.load(session)


LedgerDep = Annotated[pd.DataFrame, Depends(get_ledger)]

MonthQuery = Annotated[str | None, Query(pattern=MONTH_PATTERN,
                                         description="YYYY-MM")]


def selected_month(frame: LedgerDep, month: MonthQuery = None) -> pd.Period:
    """The requested month, or the last complete month with transactions."""
    if month is not None:
        return pd.Period(month, freq="M")

    last = ledger.last_complete_month(frame)
    if last is None:
        raise HTTPException(status_code=404, detail="No transactions")

    return last


MonthDep = Annotated[pd.Period, Depends(selected_month)]


def selected_period(frame: LedgerDep,
                    start: MonthQuery = None,
                    end: MonthQuery = None) -> tuple[pd.Period, pd.Period]:
    """The requested months, ending by default at the last complete month
    with transactions and spanning the trailing months."""
    last = selected_month(frame, end)
    first = pd.Period(start, freq="M") if start is not None \
        else last - (TRAILING_MONTHS - 1)

    if first > last:
        raise HTTPException(status_code=422,
                            detail="start must not be after end")

    return first, last


PeriodDep = Annotated[tuple[pd.Period, pd.Period], Depends(selected_period)]
