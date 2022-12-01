import dash
import calendar
import pandas as pd
import financial.entities.db as db
import plotly.graph_objs as go

from sqlalchemy.orm import Session
from pandas import DataFrame
from datetime import datetime
from dash import html, dcc
from pandas import DataFrame
from datetime import datetime

dash.register_page(__name__)


def data_frame() -> DataFrame:
    df: DataFrame = None  # type:ignore
    df = pd.DataFrame(get_data(db.get_session()))

    return df


def get_data(session: Session):
    return session.execute(f"""
        select
            DATE_FORMAT(date, '%m-%Y') as date_ref,
            SUM(value)*-1 as sum
        from transactions
        where description LIKE '%CDB POS DI LIQ. BANCO INTER SA%'
        and date > '2021-08-31'
        group by date_ref;
    """).fetchall()


df = data_frame()
fig = go.Figure(data=[go.Scatter(x=df["date_ref"], y=df["sum"])])
layout = dcc.Graph(figure=fig)
