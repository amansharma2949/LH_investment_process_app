import dash_table
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
import dash_ui as dui
from dash.dependencies import Input, Output, State
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import plotly.graph_objects as go
from logic import *

############################################################################################

app = Dash()
external_stylesheets = ['https://codepen.io/rmarren1/pen/mLqGRg.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, )
server = app.server
my_css_urls = ["https://codepen.io/rmarren1/pen/mLqGRg.css"]

colors = {
    'background': '#414b4d',
    'text': '#7FDBFF'
}

app.layout = html.Div(children = [html.Div([html.H1('LIGHTHAVEN INVESTMENT PROCESS')],
                           style={'textAlign': 'center', 'fontSize':20}),

        # ad table
        # html.Div(children = [html.H1(children="Data Table", # html for table
        #          style= {'textAlign': 'center', 'fontSize':20}), show_data_table('AMZN')]),

        dcc.Dropdown(
            id='input',
            options=[{'label':item, 'value':item} for item in get_data_table()['Ticker'].unique()],
            value = get_data_table()['Ticker'].unique()[0],
            placeholder="Select a Ticker"
        ),

        html.Div(id = 'main_graph')
])

@app.callback(
    Output(component_id = 'main_graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)

############################################################################################

def update_graph(ticker):
    ticker_data = get_ticker_data(ticker)

    # Get stock price data
    start = datetime.datetime.today() - relativedelta(years=5)
    end = datetime.datetime.today()

    #try:
    price_data = yf.download(ticker, start, end)
    price_data = price_data.reset_index()
    #except:
    #    return "Could not get data"

############################################################################################

# Create main chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=list(price_data['Date']), y=list(price_data['Close']), name="close",
                             line=dict(color="#03b1fc", width=3)))

    def create_annotation_list(data):
        annotation_list = []

        for row in range(0, data.shape[0]):
            comment = '<b>' + data.iloc[row]['Event'] + '</b><br>' + add_new_line(data.iloc[row]['Comment'])
            date = last_trading_day(data.iloc[row]['Date']) # fix helper function to get last trading day
            price_stock = price_data[price_data['Date'] == date].iloc[0]['Close']
            new_entry = dict(
                            x=date,
                            y=price_stock,
                            text=comment,
                            showarrow=True,
                            font=dict(
                                size=12,
                                color="#414b4d"
                            ),
                            align="center",
                            arrowhead=3,
                            arrowsize=1,
                            arrowwidth=1,
                            arrowcolor="#414b4d",
                            bordercolor="#414b4d",
                            borderwidth=2,
                            borderpad=3,
                            bgcolor="#D0E4F7",
                            opacity=0.8
                            )
            annotation_list.append(new_entry)

        return annotation_list

    fig.update_layout(
        title='<b>' + ticker + ' Investment Process</b>',
        title_x=0.5,
        xaxis_title="<b>Date</b>",
        font=dict(
                size=16,
                color="black"
            ),
        yaxis_title="<b>Stock Price</b>",
        margin={'l': 50, 'r': 50, 't': 40, 'b': 40},
        annotations=create_annotation_list(ticker_data),
        height=775,
        paper_bgcolor='#03b1fc'
        )

    stock_chart = dcc.Graph(id="Stock Graph", figure=fig)

    return stock_chart

############################################################################################
# Create table
def show_data_table(ticker):
    table = create_table(get_data_table(), ticker)

    final_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in table.columns],
        data=table.to_dict('records'),
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        }
    )
    return final_table

############################################################################################

if __name__ == "__main__":
    app.run_server(debug=True)

############################################################################################
