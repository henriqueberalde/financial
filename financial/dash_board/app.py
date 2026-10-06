from dash import Dash, html, dcc
import dash

from financial import settings
from financial.constants import DASHBOARD_STYLESHEET_URL

app = Dash(
    __name__,
    external_stylesheets=[DASHBOARD_STYLESHEET_URL],
    use_pages=True
)

app.layout = html.Div(
    className="container-fluid",
    children=[
        html.Nav(
            className="navbar navbar-expand-lg navbar-dark bg-dark",
            children=[
                html.Div(
                    className="container-fluid",
                    children=[
                        html.Div(
                            className="container-fluid",
                            children=[
                                html.Ul(
                                    className="navbar-nav mr-auto",
                                    children=[
                                        html.Li(
                                            className="nav-item",
                                            children=[
                                                dcc.Link(
                                                    className="nav-link",
                                                    children=f"{page['name']}",
                                                    href=page["relative_path"]
                                                )
                                            ]
                                        )
                                        for page in dash.page_registry.values()
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ]
        ),
        dash.page_container
    ]
)

if __name__ == '__main__':
    app.run(host=settings.dashboard_host(),
            port=settings.dashboard_port(),
            debug=settings.dashboard_debug())
