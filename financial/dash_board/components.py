from dash import html
from pandas import DataFrame
from financial.constants import DASHBOARD_TABLE_MAX_ROWS


def table_content(df: DataFrame):
    return [
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), DASHBOARD_TABLE_MAX_ROWS))
        ])
    ]
