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
        select date, value
        from transactions
        where description LIKE '%CDB POS DI LIQ. BANCO INTER SA%';
    """).fetchall()


df = data_frame()
fig = go.Figure(data=[go.Scatter(x=df["date"], y=df["value"])])
layout = dcc.Graph(figure=fig)
