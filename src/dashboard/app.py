from dash import Dash, dcc, html, Input, Output, callback
import pandas
from paths import DATA_PROCESSED


tickers = pandas.read_csv(DATA_PROCESSED / 'selected_tickers.csv')

ticker_options = [
    {"label": lbl, "value": val}
    for lbl, val in zip(tickers.apply(
        lambda row: f"{row['Symbol']}: {row['Security Name']}",
        axis=1
    ), tickers.to_dict(orient="records"))
]

print(tickers.to_dict())

app = Dash()
app.layout = html.Div([
    dcc.Dropdown(options=ticker_options, value=[tickers[0]], multi=True, id='ticker-dropdown'),
    html.Div(id='dd-output-container')
])


@callback(
    Output('dd-output-container', 'children'),
    Input('ticker-dropdown', 'value')
)
def update_output(value):
    return f'You have selected {value}'


if __name__ == '__main__':
    app.run(debug=True)
