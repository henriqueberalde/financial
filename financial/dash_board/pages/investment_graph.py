import dash
import pandas as pd
import financial.entities.db as db
import plotly.graph_objs as go

from sqlalchemy import text
from financial import constants
from sqlalchemy.orm import Session
from pandas import DataFrame
from dash import dcc

dash.register_page(__name__)


def data_frame() -> DataFrame:
    df: DataFrame = None  # type:ignore
    df = pd.DataFrame(get_data(db.get_session()), columns=["date_ref", "sum"])  # nopep8

    return df


def get_data(session: Session):
    return session.execute(text("""
        select
            DATE_FORMAT(date, '%m-%Y') as date_ref,
            SUM(value)*-1 as sum
        from transactions
        where description LIKE :description_pattern
        and date > :start_date
        group by date_ref;
    """), {
        "description_pattern": constants.INVESTMENT_DESCRIPTION_PATTERN,
        "start_date": constants.INVESTMENT_START_DATE,
    }).fetchall()


df = data_frame()
fig = go.Figure(data=[go.Scatter(x=df["date_ref"], y=df["sum"])])
layout = dcc.Graph(figure=fig)
