import dash
import calendar
import pandas as pd
import financial.entities.db as db

from sqlalchemy.orm import Session
from pandas import DataFrame
from datetime import datetime
from dash import html
from pandas import DataFrame
from datetime import datetime

dash.register_page(__name__)


def table_content(df: DataFrame):
    return [
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), 1000))
        ])
    ]


def every_month() -> DataFrame:
    year = datetime.now().year

    df: DataFrame = None  # type:ignore

    for month in range(1, 13):
        start_date = datetime(year, month, 1, 0, 0, 0, 0)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, 999999)

        df_local = pd.DataFrame(grouped_spends_by_period_all(db.get_session(),
                                start_date,
                                end_date))
        if df is None:
            df = df_local
        elif len(df_local) > 0:
            df = df.merge(
                df_local,
                how="outer",
                on=("sector", "category"))  # type: ignore

    return df.sort_values(by=['sector'], na_position='first')


def grouped_spends_by_period_all(session: Session,
                                 start_date: datetime,
                                 end_date: datetime):
    return session.execute(f"""
        select
            c.sector,
            c.name as category,
            SUM(t.value) as {start_date.month}_{start_date.year}
        from transactions t
        left join categories c on c.id = t.category_id
        where t.value < 0
            and date between :start_date and :end_date
            and context is null
        group by c.name, c.sector
        order by c.sector, 3 desc;
    """, {"start_date": start_date, "end_date": end_date}).fetchall()


layout = html.Div(children=[
    html.Div(className="col-12", children=[
        html.H5(className="display-6", children='All Months'),
        html.Table(table_content(every_month()),
                   id="table_all_months",
                   className="table table-striped table-hover")
    ]),
])
