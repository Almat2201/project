"""Complete the four SpaceX dashboard checkpoint components."""
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from flask import send_file

ROOT=Path(__file__).resolve().parent
data=pd.read_csv(ROOT/'spacex_launch_dash.csv')
app=Dash(__name__)
app.title='SpaceX Launch Outcomes'
app.layout=html.Div([
    html.H1('SpaceX Launch Outcomes',style={'textAlign':'center'}),
    html.Label('Launch site'),
    dcc.Dropdown(id='site-dropdown',options=[{'label':'All Sites','value':'ALL'}]+[
        {'label':site,'value':site} for site in sorted(data['Launch Site'].unique())],
        value='ALL',placeholder='Select a Launch Site here',searchable=True,clearable=False),
    html.Label('Payload mass range (kg)'),
    dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,value=[0,10000],
                    marks={i:str(i) for i in range(0,10001,2000)}),
    html.Div([dcc.Graph(id='success-pie-chart'),dcc.Graph(id='success-payload-scatter-chart')],
             style={'display':'grid','gridTemplateColumns':'1fr 1fr'}),
    html.A('Open launch-site map and coastline distance',href='/launch-map')
],style={'fontFamily':'Arial, sans-serif','maxWidth':1850,'padding':20,'margin':'auto'})

@app.callback(Output('success-pie-chart','figure'),Input('site-dropdown','value'))
def get_pie_chart(site):
    if site=='ALL':
        counts=data.groupby('Launch Site',as_index=False)['class'].sum()
        return px.pie(counts,names='Launch Site',values='class',title='Successful Launches by Site')
    selected=data.loc[data['Launch Site'].eq(site)]
    counts=selected['class'].map({0:'Failure',1:'Success'}).value_counts().rename_axis('Outcome').reset_index(name='Count')
    return px.pie(counts,names='Outcome',values='Count',title=f'Launch Outcomes · {site}')

@app.callback(Output('success-payload-scatter-chart','figure'),
              [Input('site-dropdown','value'),Input('payload-slider','value')])
def get_scatter_chart(site,payload_range):
    selected=data.loc[data['Payload Mass (kg)'].between(*payload_range)]
    if site!='ALL':
        selected=selected.loc[selected['Launch Site'].eq(site)]
    return px.scatter(selected,x='Payload Mass (kg)',y='class',color='Booster Version Category',
                      hover_data=['Launch Site'],title='Payload and Launch Outcome',
                      labels={'class':'Outcome (0 = failure, 1 = success)'})

@app.server.route('/launch-map')
def launch_map():
    return send_file(ROOT/'launch_map.html')

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8051,debug=False)
