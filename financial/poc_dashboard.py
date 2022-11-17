# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import financial.entities.db as db

from sqlalchemy.orm import Session
from pandas import DataFrame
from dash import Dash, html, dcc, Output, Input
from datetime import datetime
from financial.entities.transaction import Transaction
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


empty_result = "No Data"
external_css = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"  # nopep8

app = Dash(__name__, external_stylesheets=[external_css])


def transaction_spends_by_period(session: Session,
                                 start_date: datetime,
                                 end_date: datetime):
    return session.execute("""
        select
            t.id,
            t.date,
            t.description,
            c.name,
            t.value
        from transactions t
        left join categories c on c.id = t.category_id
        where t.value < 0
        and date between :start_date and :end_date
        order by date desc;
    """, {"start_date": start_date, "end_date": end_date}).fetchall()


def all_transactions_by_period(session: Session,
                               start_date: datetime,
                               end_date: datetime):
    return session.execute("""
        select
            t.id,
            t.date,
            t.description,
            c.name,
            t.original_value as value
        from transactions t
        left join categories c on c.id = t.category_id
        where date between :start_date and :end_date
        order by date desc;
    """, {"start_date": start_date, "end_date": end_date}).fetchall()


def grouped_spends_by_period(session: Session,
                             start_date: datetime,
                             end_date: datetime):
    return session.execute("""
        select
            c.name as category,
            SUM(t.value)  as value_spent
        from transactions t
        left join categories c on c.id = t.category_id
        where t.value < 0
            and date between :start_date and :end_date
        group by c.name
        order by 2;
    """, {"start_date": start_date, "end_date": end_date}).fetchall()


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


def grouped_spends_df(start_date: datetime, end_date: datetime):
    grouped_spends_df = pd.DataFrame(
        grouped_spends_by_period(db.get_session(),
                                 start_date,
                                 end_date)
    )
    return grouped_spends_df


def spends_transactions_df(start_date: datetime, end_date: datetime):
    spends_transactions_df = pd.DataFrame(
        transaction_spends_by_period(db.get_session(),
                                     start_date,
                                     end_date)
    )

    if len(spends_transactions_df) == 0:
        return spends_transactions_df

    total_value = spends_transactions_df["value"].sum()
    total_df = DataFrame([{
        "": "",
        "": "",
        "": "",
        "name": "Total",
        "value": total_value
    }])
    spends_transactions_df = pd.concat([
        spends_transactions_df,
        total_df], axis=0)

    return spends_transactions_df


def all_transactions_df(start_date, end_date):
    return pd.DataFrame(
        all_transactions_by_period(db.get_session(),
                                   start_date,
                                   end_date)
    )


app.layout = html.Div(
    className="container-fluid",
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(className="col-12", children=[
                    html.Form(children=[
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            display_format="DD/MM/YYYY")
                    ]),
                ]),
                html.Div(className="col-4", children=[
                    html.H1(className="display-6", children='Grouped Spends'),
                    html.Table(None,
                               id="table_grouped_spends",
                               className="table table-striped table-hover")
                ]),
                html.Div(className="col-8", children=[
                    html.H1(className="display-6", children='Graph'),
                    dcc.Graph(id="graph")
                ]),
                html.Div(className="col-12", children=[
                    html.H1(className="display-6",
                            children='Spend Transactions'),
                    html.Table(None,
                               id="table_spends_transactions",
                               className="table table-striped table-hover")
                ]),
                html.Div(className="col-12", children=[
                    html.H1(className="display-6",
                            children='All Transactions (no filter or normalizations)'),  # nopep8
                    html.Table(None,
                               id="table_all_transactions",
                               className="table table-striped table-hover")
                ]),
            ]
        )
    ]
)


@app.callback(
    Output('table_grouped_spends', 'children'),
    Output('graph', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_grouped_spends(start_date, end_date):
    if not has_date_range(start_date, end_date):
        return empty_result, go.Figure()

    df = grouped_spends_df(start_date, end_date)

    last_month_start_date = parse(start_date) + relativedelta(months=-1)
    last_month_end_date = parse(end_date) + relativedelta(months=-1)

    last_month_df = grouped_spends_df(last_month_start_date,
                                      last_month_end_date)

    merged = last_month_df.merge(df, how='outer', on='category')

    if len(merged) == 0:
        return empty_result, go.Figure()

    # fig = go.Figure(
    #     data=[
    #         go.Scatter(name='ronaldo', x=[1, 2, 3], y=[4, 1, 2]),
    #         go.Scatter(name='rivaldo', x=[1, 2, 3], y=[9, 5, 2])
    #     ]
    # )

    scatters = []
    x = merged.columns.values.tolist()[1:3]

    for row in merged.iterrows():
        category = row[1]["category"]
        value_spent_x = row[1]["value_spent_x"]
        value_spent_y = row[1]["value_spent_y"]
        y = [abs(value_spent_x), abs(value_spent_y)]
        scatters.append(go.Scatter(name=category, x=x, y=y))

    fig = go.Figure(data=scatters)

    # total_value = merged["value_spent"].sum()
    # total_df = DataFrame([{
    #     "category": "Total",
    #     "value_spent": total_value
    # }])
    # grouped_spends_df = pd.concat([grouped_spends_df, total_df], axis=0)

    return table_content(merged), fig


@app.callback(
    Output('table_spends_transactions', 'children'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_spends_transactions(start_date, end_date):
    if not has_date_range(start_date, end_date):
        return empty_result

    df = spends_transactions_df(start_date, end_date)

    if len(df) == 0:
        return empty_result

    return table_content(df)


@app.callback(
    Output('table_all_transactions', 'children'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_all_transactions(start_date, end_date):
    if not has_date_range(start_date, end_date):
        return empty_result

    df = all_transactions_df(start_date, end_date)

    if len(df) == 0:
        return empty_result

    return table_content(df)


def has_date_range(start_date, end_date):
    if start_date is None:
        return False

    if end_date is None:
        return False

    return True


if __name__ == "__main__":
    app.run_server(debug=True)
