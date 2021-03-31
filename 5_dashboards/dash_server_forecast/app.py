'''
Created on Jan 21, 2021

@author: mrmopoz
'''
import dash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,suppress_callback_exceptions=True,  external_stylesheets=external_stylesheets)

#app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server