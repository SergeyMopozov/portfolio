'''
Created on Feb 18, 2021

@author: mrmopoz
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
#import plotly.express as px
#import plotly.graph_objects as go



def cusum(data, threshold=4):

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
        if high_sum > threshold : #or low_sum < -threshold
            anomalies.append((index_names[index], item.tolist()))
            
            
    anomalies = pd.DataFrame(anomalies, columns=['date', 'value']).explode('value')
    cusum = data
    cusum = cusum.assign(High_Cusum=high_sum_final, Low_Cusum=low_sum_final)
    
    return anomalies


def preapare_data(data, mmpo, product):
    
    start_day = (datetime.today() - pd.to_timedelta(720, unit='d')).strftime('%Y-%m-%d')

    backlog_load = data[(data['mmpo_index'] == mmpo) & (data['type_product'] == product)]
    backlog_load = backlog_load.pivot(index='date_', 
                                      columns='type_product', 
                                      values=['input_', 'output_', 'percentile_50', 'percentile_85']).fillna(0)#.reset_index()
    backlog_load.columns = [col[0] + '_' + str(col[1]) for col in backlog_load.columns.to_flat_index()]
    backlog_load = backlog_load.resample('H').asfreq(0)
    
    processing_time = (backlog_load.filter(like='percentile') / 24).resample('D').mean()
    
    input_load = backlog_load.filter(like='input').resample('D').sum()
    output_load = backlog_load.filter(like='output').resample('D').sum()
    
    backlog_load = input_load.cumsum().sub(output_load.cumsum().values)
    backlog_load.columns = [col.replace('input', 'backlog') for col in backlog_load.columns]
    
    return backlog_load.loc[start_day:], input_load.loc[start_day:], output_load.loc[start_day:], processing_time.loc[start_day:]


def mmpo_rating(data):
    start_day = (datetime.today() - pd.to_timedelta(45, unit='d')).strftime('%Y-%m-%d')
    rang = data[(data['date_'] > start_day) &\
                (data['type_product']  != 'domestic')] \
            .groupby(['mmpo_index'],as_index=False)\
            .sum()\
            .query('input_ > 0')\
            .sort_values('input_', ascending=True).tail(10)
    rang['mmpo_index'] = rang['mmpo_index'].astype(str) + '_'
    bars = [dict(
            x=rang['input_'],
            y=rang['mmpo_index'],
            type = 'bar',
            orientation='h'
            )] 
    return {
        'data': bars,
        'layout': dict(
                        xaxis={'title': 'Количество отправлений'},
                        yaxis={'title': 'Топ-10 ММПО за последний месяц'},
                        margin={'l': 120, 'b': 40, 't': 40, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500})
        
        }

def events_traces(events, max_level):
    ev_tr = []
    start_day = (datetime.today() - pd.to_timedelta(540, unit='d')).strftime('%Y-%m-%d')
    events = events.query("ds_min > @start_day")
    
    for _, row in events.iterrows():
    
        ev_tr.append(dict( x=[row['ds_min'], row['ds_min']],
                           y=[0, max_level],
                           mode='lines',
                           name=row['event_'],
                           line=dict(width=4)))
        
#         ev_tr.append(dict(
#                          x0=row['ds_min'], x1=row['ds_max'],
#                          opacity=0.5, fillcolor="LightSalmon",
#                          layer="below", line_width=0, name=row['event_']))

    return ev_tr

# # load data
data = pd.read_pickle('/home/mrmopoz/jupyter_notebooks/work_projects/forecast/SLA/in_out_streams.pckl')
mmpo_descript = pd.read_csv('/home/mrmopoz/jupyter_notebooks/work_projects/forecast/SLA/mmpo.csv')
events = pd.read_pickle('/home/mrmopoz/jupyter_notebooks/work_projects/forecast/SLA/events.pckl')
# 
# # dropdown list values
mmpo = [{'label': str(item) + '-' + mmpo_descript[mmpo_descript['INDEX']==item]['OPSNAME'].iloc[0], 
         'value': item } for item in sorted(data['mmpo_index'].unique())]

products = [{'label': item, 'value': item } for item in sorted(data['type_product'].unique())]

events_button =[{'label': 'Отображать', 'value':'True'}, {'label': 'Неотображать', 'value':'False'}]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# create app layout  div-right-panel
app.layout = html.Div(className="eleven columns", 
    children=[
    html.H1(children='Анализ структуры и аномальных отклонений остатков (бэклогов) в ММПО'),
    dcc.Markdown('Данный отчет позволяет анализировато загрузку ММПО и выявлять аномалии ' + \
                  'в формировании бэклогов'),  
     # filter panel
     html.Div(className="row",
                 children =[
                            html.Div(children =[
                                    html.H3('ММПО'),
                                    dcc.RadioItems(
                                        id='mmpo',
                                        options=mmpo,
                                        value='')],
                                className="six columns"),
                            
                            html.Div(children =[
                                    html.H3('Продукт', ),
                                    dcc.RadioItems(
                                        id='type_product',
                                        options=products,
                                        value='')],
                                className="six columns"), 
                            
                            html.Div(children =[
                                    html.H3('Распродажи', ),
                                    dcc.RadioItems(
                                        id='events_button',
                                        options=events_button,
                                        value='False')],
                                className="six columns"), 
                            

        ]),
        
    
    # chart parts
    html.Div(className="row",
             children =[
                        html.Div([ dcc.Graph(id='mmpo_dist', figure=mmpo_rating(data))], className="six columns"),
                        html.Div([ dcc.Graph(id='product_dist')], className="six columns"),
                        
    ]),
    
    html.Div(className="row",
             children =[
                        html.Div(
                            children =[
                                dcc.Graph(id='count_backlog'),
                                dcc.Graph(id='processing_time'),
                               
                                ], className="six columns"),
                        
                        html.Div(
                            children =[
                                dcc.Graph(id='count_input'),
                                dcc.Graph(id='count_output')
                                ], className="six columns")
            ])
    
    ])
    

# update chart 1 

@app.callback(
    [Output('count_backlog', 'figure'), Output('count_input', 'figure'), 
     Output('count_output', 'figure'), Output('processing_time', 'figure')],
    [Input('mmpo', 'value'), Input('type_product', 'value'), Input('events_button','value')])
    
def update_figure_chart_1(mmpo, product, events_butt):
    
    backlog_load, input_load, output_load, processing_time = preapare_data(data, mmpo, product)
    
    traces = []
    window_size=28*3
    for df in [backlog_load, input_load, output_load]:
        trace = []
        for val in df.columns:
            trace.append(dict(
                                    x=df.index,
                                    y=df[val],
                                    mode='lines',
                                    name=val))
                
            trace.append(dict(
                                    x=df.index,
                                    y=df[val].rolling(window_size).mean(),
                                    mode='lines',
                                    name='Move AVG'))
                
            trace.append(dict(
                                    x=df.index,
                                    y=df[val].rolling(window_size).mean() + df[val].rolling(window_size).std() * 3,
                                    mode='lines',
                                    name='Upper bound'))
                
                         
            anomalies = cusum(df[[val]])
            trace.append(dict(
                                    x=anomalies['date'],
                                    y=anomalies['value'],
                                    mode='markers',
                                    marker = {'color':'rgba(255, 17, 0, .8)',
                                              'size' : 10},
                                    name='Anomalies'))
            
            if events_butt == 'True':
                for e in events_traces(events, df[val].max()):
                    trace.append(e)
            
        traces.append(trace)
    
    #tracae for time
    trace = []
    max_time = 0
    for val in processing_time.columns:    
        trace.append(dict(
                                         x=processing_time.index,
                                         y=processing_time[val],
                                         mode='lines',
                                         name=val))
        anomalies = cusum(processing_time[[val]])
        trace.append(dict(
                                         x=anomalies['date'],
                                         y=anomalies['value'],
                                         mode='markers',
                                         marker = {'color':'rgba(255, 17, 0, .8)',
                                                   'size' : 10},
                                         name='Anomalies'))
        max_time = processing_time[val].max()
    
    if events_butt == 'True':
        for e in events_traces(events, max_time):
            trace.append(e)
        
    traces.append(trace)   

    return [{
        'data': traces[0],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Накопление отправлений внутри ММПО'},
                        margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500})
        
        }, {
        'data': traces[1],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Входящий поток'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),
        }, {
        'data': traces[2],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Исходящий поток'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),   
        },{
        'data': traces[3],
        'layout': dict(
                        xaxis={'title': 'Дата'},
                        yaxis={'title': 'Время обработки, суток'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500}),   
        }]


# @app.callback(
#     [Output('processing_time', 'figure')],
#     [Input('mmpo', 'value'), Input('type_product', 'value')])
# 
# def update_time(mmpo, product):
#     
#     _, _, _, processing_time = preapare_data(data, mmpo, product)
#     fig = go.Figure()
#     
#     for val in processing_time.columns:    
#         fig.append_trace(x=processing_time.index,
#                       y=processing_time[val],
#                      mode='lines',
#                      name=val)
#         
#         anomalies = cusum(processing_time[[val]])
#         fig.append_trace(x=anomalies['date'],
#                       y=anomalies['value'],
#                         mode='markers',
#                         marker = {'color':'rgba(255, 17, 0, .8)',
#                                   'size' : 10},
#                         name='Anomalies')
#     
#     
#     for _, row in events.iterrows():
#              
#         fig.add_vrect(x0=row['ds_min'], x1=row['ds_max'],
#                          opacity=0.5, fillcolor="LightSalmon",
#                          layer="below", line_width=0, name=row['event_'])  
#         
#     return [fig]
# update chart 2
 
@app.callback(
    [Output('product_dist', 'figure')],
    [Input('mmpo', 'value')])
    
def update_figure_chart_2(mmpo):

    start_day = (datetime.today() - pd.to_timedelta(30, unit='d')).strftime('%Y-%m-%d')
    rang = data[(data['date_'] > start_day) &\
                 (data['mmpo_index']==mmpo) &\
                 (data['type_product']  != 'domestic')] \
            .groupby(['mmpo_index', 'type_product'],as_index=False)\
            .sum()\
            .query('input_ > 0')\
            .sort_values('input_', ascending=True).tail(10)
            
            
#     rang = data[(data['date_'] > start_day) &\
#                  (data['mmpo_index']==mmpo)] \
#             .groupby(['mmpo_index', 'type_product'],as_index=False)\
#             .sum()\
#             .query('input_ > 0')\
#             .sort_values('input_', ascending=True).tail(10)            

    bars = [dict(
            x=rang['input_'],
            y=rang['type_product'],
            type = 'bar',
            orientation='h'
            )] 
    return [{
        'data': bars,
        'layout': dict(
                        xaxis={'title': 'Количество отправлений'},
                        yaxis={'title': 'Топ-10 продуктов в ММПО за последний месяц' },
                        margin={'l': 160, 'b': 40, 't': 40, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest',
                        transition = {'duration': 500})
        
        }]
    
    
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False, port=8050, host='0.0.0.0')
    
    