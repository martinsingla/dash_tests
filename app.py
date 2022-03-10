from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd
import numpy as np

from anpact_scrapper import get_ANPACTdb_full_data, get_forecastsdb

import warnings
warnings.filterwarnings("ignore")

#===========================================================================
app = Dash(__name__)
server = app.server 

#GET HISTORIC DATA FROM MONGODB
dat= get_ANPACTdb_full_data()

dat['date'] = pd.to_datetime(dat['date'])
dat['year'] = dat['date'].dt.year
dat['quarter'] = dat['date'].dt.quarter
dat['month'] = dat['date'].dt.month
dat= dat[['year', 'quarter', 'month', 
          'truck4_5_ANPACT', 'truck6', 'truck7', 'truck8', 'truckTractor',
          'bus5_6', 'bus7', 'bus8', 'busLongDist']]

#Split historics & new sales data reported
hist= dat[dat['year'] < 2022]
new_dat= dat[dat['year']>= 2022].reset_index(drop=True)

#GET FORECASTS FROM MONGODB
#fcst= NEW_FUNCTION_TO_DEFINE()  #####<<<<------- HAY QUE TERMINAR FCSTS DE BUSES ANTES!!!!

##PROVISIONAL
fcst= get_forecastsdb()
fcst['year'] = pd.to_datetime(fcst['date']).dt.year
fcst['quarter'] = pd.to_datetime(fcst['date']).dt.quarter
fcst['month'] = pd.to_datetime(fcst['date']).dt.month
fcst= fcst[['year', 'quarter', 'month', 'truck4_5_ANPACT', 'truck6', 'truck7', 'truck8', 'truckTractor',
           'bus5_6', 'bus7', 'bus8', 'busLongDist']]
fcst= fcst[fcst['year']>= 2022].reset_index(drop=True)

##UNIFY FORECASTS & HISTORIC
dat = pd.concat([hist, fcst])
    
for i in new_dat.columns[3:]:
    new_dat= new_dat.rename(columns= {i: 'nd_'+i})

dat= pd.merge(dat, new_dat, on= ['year', 'quarter', 'month'], how='left')
for seg in ['truck4_5_ANPACT', 'truck6', 'truck7', 'truck8', 'truckTractor',
           'bus5_6', 'bus7', 'bus8', 'busLongDist']:
    dat.loc[(dat['year'] == 2021) & (dat['month'] == 12), 'nd_'+seg] = dat.loc[(dat['year'] == 2021) & (dat['month'] == 12), seg]

#===========================================================================
colors= {
    'truck4_5_ANPACT': '#EF553B',
    'truck6': '#00CC96',
    'truck7': '#AB63FA',
    'truck8': '#FFA15A',
    'truckTractor': '#636EFA',
    
    'Forecast truck4_5_ANPACT': '#EF553B',
    'Forecast truck6': '#00CC96',
    'Forecast truck7': '#AB63FA',
    'Forecast truck8': '#FFA15A',
    'Forecast truckTractor': '#636EFA',
    
    'nd_truck4_5_ANPACT': '#FF6692',
    'nd_truck6': '#B6E880',
    'nd_truck7': '#FF97FF',
    'nd_truck8': '#FECB52',
    'nd_truckTractor': '#19D3F3',
    
    'bus5_6': '#EF553B', 
    'bus7': '#00CC96', 
    'bus8': '#AB63FA', 
    'busLongDist': '#FFA15A',
    
    'Forecast bus5_6': '#EF553B', 
    'Forecast bus7': '#00CC96', 
    'Forecast bus8': '#AB63FA', 
    'Forecast busLongDist': '#FFA15A',
    
    'nd_bus5_6': '#FF6692', 
    'nd_bus7': '#B6E880', 
    'nd_bus8': '#FF97FF', 
    'nd_busLongDist': '#FECB52'
}

#===========================================================================
##App Layoyt

app.layout = html.Div([
    
    html.Div([
        html.Br(),
        html.H2('Mexican CV Market (Forecasts to 2032)', style={'margin-left': '5%',
                                                                'margin-right': 'auto', 
                                                                'display': 'block-inline',
                                                                'font-family': 'Calibri', 'color': 'white'}),
        html.Hr()
    ], style={'background-color': 'dodgerblue',
             'font-color': 'white'}),
    
    ##Selectors & Sliders DIv
    html.Div([
        html.Br(),
        html.Div([
            html.P('Select time scale:', style= {'font-size': '11px', 'font-weight': 'bold'}),
            dcc.Dropdown(
            [{'label':'Yearly', 'value': 'year'}, 
             {'label':'Quarterly', 'value': 'quarter'}, 
             {'label':'Monthly', 'value': 'month'}],
            value= 'month',
            id='periodicity')
        ]),
         html.Div([
            html.P('Select CV segment/s:', style= {'font-size': '11px', 'font-weight': 'bold'}),
            dcc.Dropdown(
            [{'label': 'BUSES', 'value': 'BUSES'}, 
             {'label': 'TRUCKS', 'value': 'TRUCKS'}],
            value= ['TRUCKS'],
            multi= False,
            placeholder="Select CV segment/s",
            id='segments'),
        ]),
        html.Div([
            html.P('Select CV class/es:', style= {'font-size': '11px', 'font-weight': 'bold'}),
            dcc.Dropdown(
                [{'label': 'Class 4 + 5 (ANPACT)', 'value': 'truck4_5_ANPACT'}, 
                       {'label': 'Class 6', 'value': 'truck6'},
                       {'label': 'Class 7', 'value': 'truck7'},
                       {'label': 'Class 8', 'value': 'truck8'},
                       {'label': 'Class Tractor', 'value': 'truckTractor'}],
                value= ['truckTractor', 'truck8'],
                multi= True,
                placeholder="Select CV class/es",
                id='classes'),
        ]),
        html.Div([
            html.P('Select time range:', style= {'font-size': '11px', 'font-weight': 'bold'}),
            dcc.RangeSlider(
            min= dat['year'].min(), 
            max= dat['year'].max(),
            step=1,
            marks= {i:i if i%2==0 else '' for i in range(2008, 2033)},
            value= [2020, 2022],
            id='years')
        ]),
    ], style={'width': '30%', 
              'display': 'block-inline',
              'margin-left': '5%',
              'margin-right': 'auto', 
              'font-family': 'Calibri'}),
    
    ##Graph Div
    html.Div([
        dcc.Graph(id='ts-chart')
    ], style={'width': '60%', 
              'display': 'block-inline',
              #'margin-left': 'auto',
              #'margin-right': 'auto', 
             })
])

#===========================================================================
@app.callback(
    Output('classes', 'options'),
    Output('classes', 'value'),
    Input('segments', 'value')
)

def update_dropdown(segments):
    
    if segments == 'TRUCKS':
        
        options_list= [{'label': 'Class 4 + 5 (ANPACT)', 'value': 'truck4_5_ANPACT'}, 
                       {'label': 'Class 6', 'value': 'truck6'},
                       {'label': 'Class 7', 'value': 'truck7'},
                       {'label': 'Class 8', 'value': 'truck8'},
                       {'label': 'Class Tractor', 'value': 'truckTractor'}]
        value_list= ['truckTractor', 'truck8']
        
    elif segments == 'BUSES':
        
        options_list= [{'label': 'Class 5 + 6', 'value': 'bus5_6'}, 
                       {'label': 'Class 7', 'value': 'bus7'},
                       {'label': 'Class 8', 'value': 'bus8'},
                       {'label': 'Class Long Distance', 'value': 'busLongDist'}]
        value_list= ['busLongDist', 'bus8', 'bus7', 'bus5_6']
        
    return options_list, value_list

#===========================================================================

@app.callback(
    Output('ts-chart', 'figure'),
    Input('periodicity', 'value'),
    Input('classes', 'value'),
    Input('years', 'value')
)

def update_graph(periodicity, classes, years):
    
    if periodicity == 'year':
        
        dff= dat[np.append(['year'], classes)]\
                .groupby('year', as_index=False)[classes].sum()
        dff= dff.loc[(dff['year'] >= years[0]) & (dff['year'] <= years[1])].reset_index(drop=True)
        if years[1] >= 2022:
            for seg in classes:
                dff['Forecast '+seg] = np.append(np.repeat(np.nan, len(dff.loc[(dff['year'] >= years[0]) & (dff['year'] < 2021), seg])),
                                                 dff.loc[(dff['year'] >= 2021) & (dff['year'] <= years[1]), seg])
                dff.loc[(dff['year'] >= 2022) & (dff['year'] <= years[1]), seg] = np.nan
        fig= px.line(dff, x= 'year', y= dff.columns[1:], markers= True,
                    color_discrete_sequence = [colors[col] for col in dff.columns[1:]])
        if years[1] >= 2022:
            for n in range(int(len(fig.data)/2), len(fig.data)):
                fig.data[n]['line']['dash'] = 'dot'

    elif periodicity == 'quarter':
        dff= dat[np.append(['year', 'quarter'], classes)]
        dff= dff.loc[(dff['year'] >= years[0]) & (dff['year'] <= years[1]), :].reset_index(drop=True)
        if years[1] >= 2022:
            for seg in classes:
                dff['Forecast '+seg] = np.append(np.repeat(np.nan, len(dff.loc[(dff['year'] >= years[0]) & (dff['year'] < 2021), seg])),
                                                 dff.loc[(dff['year'] >= 2021) & (dff['year'] <= years[1]), seg])
        dff['yq'] = pd.PeriodIndex([str(dff['year'][i])+'-Q'+str(dff['quarter'][i]) for i in range(0, len(dff))], freq='Q').to_timestamp()
        dff= dff.groupby('yq', as_index=False)[dff.columns[2:]].sum()
        dff.loc[(dff['yq'].dt.year < 2021) | ((dff['yq'].dt.year == 2021) & (dff['yq'].dt.quarter < 4)), ['Forecast '+seg for seg in classes]] = np.nan
        dff.loc[dff['yq'].dt.year >= 2022, classes] = np.nan
        fig= px.line(dff, x= 'yq', y= dff.columns[1:], markers= True,
                    color_discrete_sequence = [colors[col] for col in dff.columns[1:]])
        if years[1] >= 2022:
            for n in range(int(len(fig.data)/2), len(fig.data)):
                fig.data[n]['line']['dash'] = 'dot'

    elif periodicity == 'month':

        dff= dat[np.append(['year', 'month'], classes)]
        dff= dff.loc[(dff['year'] >= years[0]) & (dff['year'] <= years[1]), :].reset_index(drop=True)
        if years[1] >= 2022:
            for seg in classes:
                dff['Forecast '+seg] = np.append(np.repeat(np.nan, len(dff.loc[(dff['year'] >= years[0]) & (dff['year'] < 2021), seg])),
                                                 dff.loc[(dff['year'] >= 2021) & (dff['year'] <= years[1]), seg])

        dff['ym'] = pd.to_datetime([str(dff['year'][i])+'-'+str(dff['month'][i]) for i in range(0, len(dff))])
        dff= dff.groupby('ym', as_index=False)[dff.columns[2:]].sum()
        dff.loc[(dff['ym'].dt.year < 2021) | ((dff['ym'].dt.year == 2021) & (dff['ym'].dt.month < 12)), ['Forecast '+seg for seg in classes]] = np.nan
        dff.loc[dff['ym'].dt.year >= 2022, classes] = np.nan

        nd= dat[np.append(['year', 'month'], ['nd_'+seg for seg in classes])]
        nd= nd.loc[(nd['year'] >= years[0]) & (nd['year'] <= years[1]), :].reset_index(drop=True)
        nd['ym'] = pd.to_datetime([str(nd['year'][i])+'-'+str(nd['month'][i]) for i in range(0, len(nd))])

        nd= nd[np.append(['ym'], ['nd_'+seg for seg in classes])]

        dff = pd.merge(dff, nd, on = ['ym'])
        fig= px.line(dff, x= 'ym', y= dff.columns[1:], markers= True,
                     color_discrete_sequence = [colors[col] for col in dff.columns[1:]])

        if years[1] >= 2022:
            for n in range(int(len(fig.data)/3), len(fig.data)):
                fig.data[n]['line']['dash'] = 'dot'

    return fig
    
#===========================================================================

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)