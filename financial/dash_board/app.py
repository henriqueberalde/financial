from dash import Dash, html, dcc
import dash

external_css = "https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"  # nopep8

app = Dash(
    __name__,
    external_stylesheets=[external_css],
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
    app.run_server(debug=True)
