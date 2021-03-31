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
data = pd.read_pickle('/home/mrmopoz/jupyter_notebooks/work_projects/forecast/11.01.2021/total_forecast_2021-01-14.pckl')
# 
# 
# # dropdown list 1 "Factor"
factor = [{'label': 'Прогноз', 'value': 'yhat' },
          {'label': 'Тренд', 'value': 'trend' },
          {'label': 'Годовая сезонность', 'value': 'yearly' },
          {'label': 'Месячная сезонность', 'value': 'monthly' },
          {'label': 'Недельная сезонность', 'value': 'weekly' },
          {'label': 'Факт', 'value': 'fact' }]
#factor = []в
# dropdow list 2 "Category"
category =[{'label': 'Топ клиентов', 'value': 'short_customer' },
          {'label': 'Топ стран', 'value': 'short_country' },
          {'label': 'ММПО', 'value': 'mmpo' },
          {'label': 'Продукты', 'value': 'bar_code_type_s' }] 



# dropdow list 2 "Forecast value"
forecast_value = [{'label': 'Количество отправлений', 'value': 'count_rpo' } ,
                  {'label': 'Суммарная масса', 'value': 'sum_mass_kg' },
                  {'label': 'Средняя масса отправления', 'value': 'mean_mass' }]


# dropdow list 2 "Filter"
series_filter = [{'label': 'Топ клиентов', 'value': 'short_customer' },
          {'label': 'Топ стран', 'value': 'short_country' },
          {'label': 'Клиент', 'value': 'customer' },
          {'label': 'Страна', 'value': 'country' },
          {'label': 'ММПО', 'value': 'mmpo' },
          {'label': 'Продукты', 'value': 'bar_code_type_s' }]    


# dropdown list 2 "Filter value"
filter_value = []       

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = 
dash.Dash(__name__, external_stylesheets=external_stylesheets)

# create app layout  div-right-panel
#app.
layout = [html.Div(className="eleven columns", 
    children=[
    html.H1(children='Анализ компонент прогноза'),
    dcc.Markdown('Данный отчет позволяет проанализировать структуру ' + \
                  'комопнентов прогноза в разрезе категорий Старана, Клиент, Продукт, ММПО'),  
     # filter panel
    html.Div(children =[
    
        html.Div(className="six columns",
                 children =[
    
            html.Label('Сценарии'),
            dcc.RadioItems(
                id = 'scenrios',
                options=[
                    {'label': 'Реалистичный', 'value': 'real'},
                    {'label': 'Пессимистичный', 'value': 'lower'},
                    {'label': 'Оптимистичный', 'value': 'upper'}
                ],
                value='real'
            )]
        ),

        html.Div(className="six columns",
                 children =[
                            html.Div([ 
                                    html.Label('Прогнозируемый параметр', className="four columns"),
                                    dcc.Dropdown(
                                        id='Forecast_value',
                                        options=forecast_value,
                                        value='count_rpo',
                                        className="four columns"),
                                    #dcc.Markdown("Прогнозируемый параметр", className="two columns"),
                                    ],
                                className="row"), 
                     
                            html.Div([
                                    html.Label('Компонент прогноза', className="four columns"),
                                    dcc.Dropdown(
                                        id='Factor',
                                        options=factor,
                                        value='yhat',
                                        className="four columns"),
                                    #dcc.Markdown("Факторные компоненты", className="two columns"),
                                    ],
                                className="row"), 
                            
                            html.Div([
                                    html.Label('Категория', className="four columns"),
                                    dcc.Dropdown(
                                        id='Category',
                                        options=category,
                                        value='bar_code_type_s',
                                        className="four columns"),
                                    #dcc.Markdown("Категориальный компоненты", className="two columns"),
                                    ],
                                className="row"), 

                            html.Div([    
                                    html.Label('Категория для фильтрации', className="four columns"),
                                    dcc.Dropdown(
                                        id='Series_filter',
                                        options=series_filter,
                                        value='',
                                        className="four columns"),
                                    #dcc.Markdown("Выбор поля для фильтрации", className="two columns"),
                                    ],
                                className="row"), 
                            
                            html.Div([  
                                    html.Label('Значение фильтра', className="four columns"),
                                    dcc.Dropdown(
                                        id='Fliter_value',
                                        options=filter_value,
                                        value='',
                                        className="four columns"),
                                    #dcc.Markdown("Значение фильтра", className="two columns"),
                                    ],
                                className="row"),  
        ]),
        
    ]),
    # chart parts
    html.Div(
        children =[
        # column 1
        html.Div(
            className="six columns", 
            children=[
            dcc.Graph(id='count_rpo'),
            dcc.Graph(id='total_mass'),
            dcc.Graph(id='mean_mass')]),
        
        # column 2
        html.Div(
            className="six columns",
            children=[
            dcc.Graph( id='stacked_factors'),
            dcc.Graph( id='normed_stacked_factors'),
            dcc.Graph( id='stacked_category'),
            dcc.Graph( id='normed_stacked_category')
           
            ])
        ])
    ])
]

# update filter values
@app.callback(
    [Output('Fliter_value', 'options')],
    [Input('Series_filter', 'value')])
 
def update_filter_value(value):
    filter_value = []
    
    if value in data.columns:
        filter_value = [{'label': item, 'value': item } for item in data[value].unique()]
    
    return [filter_value]


# update chart 1 

@app.callback(
    [Output('count_rpo', 'figure'), Output('total_mass', 'figure'), Output('mean_mass', 'figure')],
    [Input('Factor', 'value'), Input('Series_filter', 'value'), Input('Fliter_value', 'value')])
   
def update_figure_chart_1(factor, filt, filt_value):
    
    factors = []
    traces=[]
    if factor != '':
        chart_data = data
        
        if factor == 'trend':
            factors = ['trend', 'trend_lower', 'trend_upper']
        if factor == 'weekly':
            factors = ['weekly', 'weekly_lower', 'weekly_upper']
        if factor == 'monthly':
            factors = ['monthly', 'monthly_lower', 'monthly_upper']
        if factor == 'yearly':
            factors = ['yearly', 'yearly_lower', 'yearly_upper']
        if factor == 'yhat':
            factors = ['yhat', 'yhat_lower', 'yhat_upper']
            
        today = datetime.today().strftime('%Y-%m-%d')
        end_day = (datetime.today() + pd.to_timedelta(365, unit='d')).strftime('%Y-%m-%d')
        
        if filt in chart_data.columns:
            chart_data = chart_data[chart_data[filt] == filt_value]
            
        chart_data = chart_data[chart_data['factor'].isin(factors)].groupby(['ds', 'factor'], as_index=False)\
                                                                   .agg({'count_rpo':'sum', 'sum_mass_kg':'sum', 
                                                                         'mean_mass':'mean'})
        
        chart_data = chart_data[(chart_data['ds'] > today) & (chart_data['ds'] <= end_day)]
          
        #fig = create_figure(chart_data, 'count_rpo', 'Forecast Quantity')
        for val in ['count_rpo', 'sum_mass_kg', 'mean_mass']:
            trace = []
            for f in factors:
                trace.append(dict(
                    x=chart_data[chart_data['factor'] == f]['ds'],
                    y=chart_data[chart_data['factor'] == f][val],
                    mode='lines',
                    name=f))
                
            traces.append(trace)
 
    return [{
        'data': traces[0],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Прогноз количества'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500})
        }, {
        'data': traces[1],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Прогноз массы'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),
        }, {
        'data': traces[2],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Прогноз средней массы'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),   
        }]
    
    

# update chart 2 

@app.callback(
    [Output('stacked_factors', 'figure'), Output('normed_stacked_factors', 'figure')],
    [Input('Forecast_value', 'value'), Input('Series_filter', 'value'), 
      Input('Fliter_value', 'value'), Input('scenrios', 'value')])

def update_figure_chart_2(forecast_value,  filt, filt_value, scenario):

    if scenario == 'lower':
        f_comp = ['trend_lower','yearly_lower', 'monthly_lower', 'weekly_lower']
    elif scenario == 'upper':
        f_comp = ['trend_upper', 'yearly_upper', 'monthly_upper', 'weekly_upper']
    else:
        f_comp = ['trend', 'yearly', 'monthly', 'weekly']
        
    today = datetime.today().strftime('%Y-%m-%d')
    end_day = (datetime.today() + pd.to_timedelta(365, unit='d')).strftime('%Y-%m-%d')
    
    categories = ['ds', 'factor']
    
    chart_data =  data[data['factor'].isin(f_comp)]
    
    if filt in chart_data.columns:
        if filt_value in chart_data[filt].unique():
            chart_data = chart_data[chart_data[filt] == filt_value]
    
    chart_data = chart_data.groupby(categories, as_index=False)[[forecast_value]]\
                                         .sum()\
                                         .pivot(index='ds', 
                                                columns='factor', 
                                                values=forecast_value)[f_comp]
    
    
    chart_data = chart_data.loc[today:end_day]

    traces = []
    trace = []
    for col in chart_data.columns:
        
        trace.append(dict(
            x=chart_data.index,
            y=chart_data[col],
                        
            mode='lines',
            stackgroup='one',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=col
        ))
    traces.append(trace)
    
    #create normed data
    chart_data = chart_data.abs().div(chart_data.abs().sum(axis=1), axis=0)
    trace = []
    for col in chart_data.columns:
        
        trace.append(dict(
            x=chart_data.index,
            y=chart_data[col],
                        
            mode='lines',
            stackgroup='one',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=col
        ))
    traces.append(trace)
    
    return [{
        'data': traces[0],
        'layout': dict(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Forecasted value'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition = {'duration': 500},
        )
    },
    
    {
        'data': traces[1],
        'layout': dict(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Forcasted value'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition = {'duration': 500},
        )
    }]

@app.callback(
    [Output('stacked_category', 'figure'), Output('normed_stacked_category', 'figure')],
    [Input('Forecast_value', 'value'), Input('Factor', 'value'),   Input('Category', 'value'),
     Input('Series_filter', 'value'), Input('Fliter_value', 'value'), Input('scenrios', 'value')])    
# update chart 3 
def update_figure_chart_3(forecast_value, factor, category,  filt, filt_value, scenario):
    
    if scenario == 'lower':
        factor = factor +'_lower'
    elif scenario == 'upper':
        factor = factor + '_upper'
    
    chart_data = data
    
    today = datetime.today().strftime('%Y-%m-%d')
    end_day = (datetime.today() + pd.to_timedelta(365, unit='d')).strftime('%Y-%m-%d')
    
    categories = ['ds']  
    if category != '':
        categories = categories + [category]

    if filt in chart_data.columns:
        if filt_value in chart_data[filt].unique():
            chart_data = chart_data[chart_data[filt] == filt_value]
    
    chart_data = chart_data[chart_data['factor'] == factor].groupby(categories, as_index=False)[[forecast_value]]\
                                         .sum()\
                                         .pivot(index='ds', 
                                                columns=category, 
                                                values=forecast_value)
    
    
    chart_data = chart_data.loc[today:end_day]

    traces = []
    trace = []
    for col in chart_data.columns:
        
        trace.append(dict(
            x=chart_data.index,
            y=chart_data[col],
                        
            mode='lines',
            stackgroup='one',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=col
        ))
    traces.append(trace)
    
    #create normed data
    chart_data = chart_data.abs().div(chart_data.abs().sum(axis=1), axis=0)
    trace = []
    for col in chart_data.columns:
        
        trace.append(dict(
            x=chart_data.index,
            y=chart_data[col],
                        
            mode='lines',
            stackgroup='one',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=col
        ))
    traces.append(trace)
    
    return [{
        'data': traces[0],
        'layout': dict(
            xaxis={'title': 'Дата'},
            yaxis={'title': 'Прогнозируемый параметр'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition = {'duration': 500},
        )
    },
    
    {
        'data': traces[1],
        'layout': dict(
            xaxis={'title': 'Дата'},
            yaxis={'title': 'Прогнозируемый параметр'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition = {'duration': 500},
        )
    }]
    

# if __name__ == '__main__':
#     app.run_server(debug=True)
