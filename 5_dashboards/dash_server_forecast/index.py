'''
Created on Jan 21, 2021

@author: mrmopoz
'''

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import anomaly_dash, forecast_dash


# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content')
# ])


app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    html.H1(children=[
        dcc.Link('Дашборд детекции аномалий', href='/apps/anomaly_dash'),
        html.Br(),
        dcc.Link('Дашборд краткосрочный прогноз', href='/apps/forecast_dash'),
    ]),
    # content will be rendered in this element
    html.Div(id='page-content')
])


@app.callback( 
              [Output('page-content', 'children')],
              [Input('url', 'pathname')])
def display_page(pathname):
    
    if pathname == '/apps/anomaly_dash':
        return anomaly_dash.layout

    elif pathname == '/apps/forecast_dash':
        return forecast_dash.layout
    
    else:
        return [html.Div()]
    
#     [html.Div( children=[
#                         html.H1(children='ERROR 404')])]

if __name__ == '__main__':
    app.run_server(debug=True)
     
    
    