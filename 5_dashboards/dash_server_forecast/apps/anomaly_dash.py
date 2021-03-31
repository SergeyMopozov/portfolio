'''
Created on Jan 14, 2021

@author: mrmopoz
'''
'''
Created on Jan 12, 2021

@author: mrmopoz
'''
'''
Created on May 31, 2020

@author: mrmopoz
'''
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime

from app import app


# # load data
data = pd.read_pickle('/home/mrmopoz/jupyter_notebooks/work_projects/forecast/11.01.2021/forecast_data_2021-01-18.pckl')
start_day = (datetime.today() - pd.to_timedelta(365, unit='d')).strftime('%Y-%m-%d')
data = data[data['ds'] > start_day]
# 
# # dropdown list values
customers = [{'label': item.capitalize(), 'value': item } for item in data['customer'].unique()]
countries = [{'label': item.capitalize(), 'value': item } for item in data['name_ru'].unique()]
products = [{'label': item.capitalize(), 'value': item } for item in data['bar_code_type_s'].unique()]
mmpo = [{'label': item.capitalize(), 'value': item } for item in data['region_from'].unique()]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = 
dash.Dash(__name__, external_stylesheets=external_stylesheets)

# create app layout  div-right-panel
#app.
layout = [html.Div(className="eleven columns", 
    children=[
    html.H1(children='Анализ аномалий в потоках отправлений'),
    dcc.Markdown('Данный отчет позволяет выявлять аномалии ' + \
                  'в поведении выбранного потока отправлений'),  
     # filter panel
     html.Div(className="row",
                 children =[
                            html.Div([
                                    html.Label('Клиент', className="four columns"),
                                    dcc.Dropdown(
                                        id='customer',
                                        options=customers,
                                        value='',
                                        className="four columns"),
                                    
                                    ],
                                className="row"),
                            
                            html.Div([
                                    html.Label('Страна', className="four columns"),
                                    dcc.Dropdown(
                                        id='country',
                                        options=countries,
                                        value='',
                                        className="four columns"),
                                    
                                    ],
                                className="row"), 

                            html.Div([    
                                    html.Label('Продукт', className="four columns"),
                                    dcc.Dropdown(
                                        id='product',
                                        options=products,
                                        value='',
                                        className="four columns"),
                                    #dcc.Markdown("Выбор поля для фильтрации", className="two columns"),
                                    ],
                                className="row"), 
                            
                            html.Div([  
                                    html.Label('ММПО', className="four columns"),
                                    dcc.Dropdown(
                                        id='mmpo',
                                        options=mmpo,
                                        value='',
                                        className="four columns"),
                                    #dcc.Markdown("Значение фильтра", className="two columns"),
                                    ],
                                className="row"),  
        ]),
        
    
    # chart parts
    html.Div(
        children =[
            dcc.Graph(id='count_rpo_an'),
            dcc.Graph(id='total_mass_an'),
            dcc.Graph(id='mean_mass_an')
            ])
    ])
    ]
    
def cusum(data, threshold=3):

    mean= data.iloc[:,0].mean()
    shift= data.iloc[:,0].std()
    threshold = threshold * shift
    
    high_sum = 0.0
    low_sum = 0.0
    anomalies = [] 
    high_sum_final = []
    low_sum_final = []
    index_names = data.index
    data_values = data.values
    for index, item in enumerate(data_values):
        high_sum = max(0, high_sum + item - mean - shift)
        low_sum = min(0, low_sum + item - mean + shift)
        high_sum_final.append(high_sum)
        low_sum_final.append(low_sum)
        if high_sum > threshold or low_sum < -threshold:
            anomalies.append((index_names[index], item.tolist()))
            
            
    anomalies = pd.DataFrame(anomalies, columns=['date', 'value']).explode('value')
    cusum = data
    cusum = cusum.assign(High_Cusum=high_sum_final, Low_Cusum=low_sum_final)
    return anomalies



# update chart 1 
 
@app.callback(
    [Output('count_rpo_an', 'figure'), Output('total_mass_an', 'figure'), Output('mean_mass_an', 'figure')],
    [Input('customer', 'value'), Input('country', 'value'), Input('product', 'value'), Input('mmpo', 'value')])
    
def update_figure_chart_1(customer, country, product, mmpo):
    
    chart_data = data
    group_list = ['ds']
    
    if customer != '':
        group_list.append('customer')
        chart_data = chart_data[(chart_data['customer'] == customer)]
    if country != '':
        group_list.append('name_ru')
        chart_data = chart_data[(chart_data['name_ru'] == country)]
    if product != '':
        group_list.append('bar_code_type_s')
        chart_data = chart_data[(chart_data['bar_code_type_s'] == product)]
    if mmpo != '':
        group_list.append('region_from')
        chart_data = chart_data[(chart_data['region_from'] == mmpo)]
    
    
             
    chart_data = chart_data.groupby(group_list, as_index=False)\
                           .agg({'count_rpo':'sum', 
                                 'sum_mass_kg':'sum', 
                                 'mean_mass':'mean'})
             
    chart_data = chart_data.set_index('ds').resample('D').asfreq(0)
    
           
    traces = []
    for val in ['count_rpo', 'sum_mass_kg', 'mean_mass']:
        
        trace = []
        trace.append(dict(
                            x=chart_data.index,
                            y=chart_data[val],
                            mode='lines',
                            name=val))
                 
        anomalies = cusum(chart_data[[val]])
        trace.append(dict(
                            x=anomalies['date'],
                            y=anomalies['value'],
                            mode='markers',
                            marker = {'color':'rgba(255, 17, 0, .8)',
                                      'size' : 10},
                            name='Anomalies'))
        traces.append(trace)
        
        
    return [{
        'data': traces[0],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Количество отправлений'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500})
        }, {
        'data': traces[1],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Суммарная массы'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),
        }, {
        'data': traces[2],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Cредняя масса'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),   
        }]
    
    


    
 
# if __name__ == '__main__':
#     #app.run_server(debug=True)
#     app.run_server(debug=False, port=8050, host='0.0.0.0')

