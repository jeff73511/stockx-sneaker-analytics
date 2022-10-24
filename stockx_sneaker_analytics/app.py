import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


df = pd.read_csv("StockX-Data-Contest-2019-3.csv", skipinitialspace=True)
df.columns = df.columns.str.replace(" ", "")
df["OrderDate"] = pd.to_datetime(df["OrderDate"])
df["ReleaseDate"] = pd.to_datetime(df["ReleaseDate"])
df.sort_values("OrderDate", inplace=True)
df["OrderQuantity"] = 1


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sneaker Analytics: Understand Your Sneakers!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="👟", className="header-emoji"),
                html.H1(children="Sneaker Analytics", className="header-title"),
                html.P(
                    children="Analyze the behavior of sneaker prices"
                    " and the number of sneaker sold on StockX in the US"
                    " between 2017 and 2019",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[{"label": "All", "value": "All"}]
                            + [
                                {"label": region, "value": region}
                                for region in np.sort(df.BuyerRegion.unique())
                            ],
                            value="All",
                            clearable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Brand", className="menu-title"),
                        dcc.Dropdown(
                            id="brand-filter",
                            options=[
                                {"label": brand, "value": brand}
                                for brand in df.Brand.unique()
                            ],
                            value="Yeezy",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Size", className="menu-title"),
                        dcc.Dropdown(
                            id="size-filter",
                            options=[{"label": "All", "value": "All"}]
                            + [
                                {"label": size, "value": size}
                                for size in np.sort(df.ShoeSize.unique())
                            ],
                            value="All",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Date Range", className="menu-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df.OrderDate.min().date(),
                            max_date_allowed=df.OrderDate.max().date(),
                            start_date=df.OrderDate.min().date(),
                            end_date=df.OrderDate.max().date(),
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ],
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("brand-filter", "value"),
        Input("size-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(region, brand, size, start_date, end_date):
    buyer_region = (
        (df.BuyerRegion != region) if region == "All" else (df.BuyerRegion == region)
    )
    shoe_size = (df.ShoeSize != size) if size == "All" else (df.ShoeSize == size)
    mask = (
        buyer_region
        & (df.Brand == brand)
        & shoe_size
        & (df.OrderDate >= start_date)
        & (df.OrderDate <= end_date)
    )
    filtered_data = df.loc[mask, :]
    price_chart_figure = {
        "data": [
            dict(
                type="lines",
                x=filtered_data["OrderDate"],
                y=filtered_data["SalePrice"],
                hovertemplate="$%{y:.2f}<extra></extra>",
                transforms=[
                    dict(
                        type="aggregate",
                        groups=filtered_data["OrderDate"],
                        aggregations=[
                            dict(target="y", func="avg", enabled=True),
                        ],
                    )
                ],
            )
        ],
        "layout": {
            "title": {
                "text": "Average Price of Sneakers",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            dict(
                type="lines",
                x=filtered_data["OrderDate"],
                y=filtered_data["OrderQuantity"],
                transforms=[
                    dict(
                        type="aggregate",
                        groups=filtered_data["OrderDate"],
                        aggregations=[
                            dict(target="y", func="sum", enabled=True),
                        ],
                    )
                ],
            )
        ],
        "layout": {
            "title": {
                "text": "Sneakers Sold",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
