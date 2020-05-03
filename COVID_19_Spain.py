# Import Built in modules
import json # JSON files utilities

# pandas and geopandas
import pandas as pd
import geopandas as gpd

#numpy
import numpy as np

#dash, to build the app
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output,Input

# Import my backend module
from AppBackend import processdata

###################################################################################
#
#
# THIS SECTION OF THE MODULE DOWNLOADS THE DATA AND PROCESS IT INTO DATAFRAMES

# Tuples to store the names and codes of the CCAA
CCAA_dict = processdata.make_CCAA_dict()
CCAA_names_tuple = tuple( sorted(CCAA_dict.keys()) )
CCAA_codes_tuple = tuple( sorted(CCAA_dict.values()) )

# Dictionary relating "cartographic ID numbers":"ISO CODES"
CCAA_cartodb_ID_dict = processdata.make_CCAA_cartodb_ID_dict()


# Code to obtain the COVID data from the ministry of health web page
#
# - data_COVID19_spain = data frame with all the data for spain
# - data_COVID19_spain_last = data frame with the last update
# - communities_data_frames_dict = dictionary containing data frames for
#                                    every community. {'name':dataframe.}
# - data_COVID19_spain_sum = data frame for the total data in Spain, i.e.,
#                            summed over the communities.

# url for the data and name for the csv file
data_url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'
data_file_name = 'data.csv'

# Download the data csv file and make the national and regional data frames
processdata.downloadDATA(data_url,data_file_name)
data_COVID19_spain = processdata.makeNationalDataFrame()
data_COVID19_columns = data_COVID19_spain.columns.to_list()

# Column names for the data
ISO_code_column_name = data_COVID19_columns[0]
date_column_name = data_COVID19_columns[1]
# Nota: El los datos de casos acumulados estan en la columna de PCR positiva para algunas CCAA
# sumar las PCR a la columna de Acumulados
cases_column_name = data_COVID19_columns[2]
PCR_column_name = data_COVID19_columns[3]
TestAC_column_name = data_COVID19_columns[4]
Hospitalized_column_name = data_COVID19_columns[5]
UCI_column_name = data_COVID19_columns[6]
deaths_column_name = data_COVID19_columns[7]
recovered_column_name = data_COVID19_columns[8]
activeCases_column_name = 'Casos Activos'


# Nota: El los datos de casos acumulados estan en la columna de PCR positiva para algunas CCAA
# sumar las PCR a la columna de Acumulados
cases_0value_mask = data_COVID19_spain[cases_column_name] == 0
data_COVID19_spain.loc[cases_0value_mask,cases_column_name] = data_COVID19_spain.loc[cases_0value_mask,PCR_column_name]
# Make a column for the ACTIVE cases
data_COVID19_spain[activeCases_column_name] = data_COVID19_spain[cases_column_name] - data_COVID19_spain[deaths_column_name] - data_COVID19_spain[recovered_column_name]

# Data set with the last update
data_COVID19_spain_last = pd.DataFrame(data_COVID19_spain[data_COVID19_spain[date_column_name]==max(data_COVID19_spain[date_column_name])])
data_COVID19_spain_last.reset_index(drop=True,inplace=True)
# add a colum for the cartodb_id
data_COVID19_spain_last['cartodb_id'] = [CCAA_cartodb_ID_dict[code] for code in data_COVID19_spain_last['CCAA']]


# Dictionary with a dataframe for everey comunidad autonoma
communities_data_frames_dict = processdata.makeCommunitiesDataFrameDict(data_COVID19_spain)

# Data set with the sum of cases for every community
dates_list = list(dict.fromkeys(data_COVID19_spain[date_column_name]))
dates_list.sort()
data_COVID19_spain_sum = pd.DataFrame(
    {
        date_column_name:dates_list,
        cases_column_name: sum( df[cases_column_name] for df in communities_data_frames_dict.values() ),
        deaths_column_name: sum( df[deaths_column_name] for df in communities_data_frames_dict.values() ),
        recovered_column_name: sum( df[recovered_column_name] for df in communities_data_frames_dict.values() ),
        activeCases_column_name: sum( df[activeCases_column_name] for df in communities_data_frames_dict.values() )
    }
)

# Load the geojson with the geometry of Spain CCAA
with open('ign_spanish_adm1_ccaa_displaced_canary.json') as file:
    mapGeoJSON_DATA = json.load(file)
type(mapGeoJSON_DATA)

###################################################################################
#
#
# THIS SECTION OF THE MODULE CREATES THE COMPONENTS

# Widget for the plot of evolution of COVID in SPAIN
nationalEvolutionFig = go.Figure(
    layout = go.Layout(
        legend=dict(
            x=0,
            y=1
        ),
        xaxis =  {
            'showgrid': False
        },
        yaxis =  {
            'showgrid': False
        },
        title="Evolución a nivel nacional",
        yaxis_title="Casos",
        xaxis_title=""
    )
)
nationalEvolutionFig.add_trace(
    go.Scatter(
        x=data_COVID19_spain_sum[date_column_name], y=data_COVID19_spain_sum[activeCases_column_name],
        mode='none',
        line=dict(width=0.5, color='rgb(131, 90, 241)'),
        name = activeCases_column_name,
        stackgroup='one' # define stack group
    )
)
nationalEvolutionFig.add_trace(
    go.Scatter(
        x=data_COVID19_spain_sum[date_column_name], y=data_COVID19_spain_sum[deaths_column_name],
        mode='none',
        line=dict(width=0.5, color='rgb(131, 90, 241)'),
        name = deaths_column_name,
        stackgroup='one' # define stack group
    )
)
nationalEvolutionFig.add_trace(
    go.Scatter(
        x=data_COVID19_spain_sum[date_column_name], y=data_COVID19_spain_sum[recovered_column_name],
        mode='none',
        line=dict(width=0.5, color='rgb(131, 90, 241)'),
        name = recovered_column_name,
        stackgroup='one' # define stack group
    )
)

nationalEvolutionGraph = dcc.Graph(
        id='nationalEvolutionComponent',
        figure=nationalEvolutionFig,
        config = {'modeBarButtonsToRemove': ['pan2d','zoom2d','zoomIn2d','zoomOut2d','hoverClosestCartesian','autoScale2d','resetScale2d','toggleSpikelines']}
    )

nationalEvolutionBox_children = [nationalEvolutionGraph]
nationalEvolutionBox = html.Div(
    children = nationalEvolutionBox_children,
    className = 'col-lg-6'
)


########################################


#########################################



dropdownCCAA = dcc.Dropdown(
    id = 'dropdownCCAA',
    options = [{'label':CCAA,'value':CCAA} for CCAA in CCAA_names_tuple],
    value = CCAA_names_tuple[0],
    placeholder = 'Comunidad autónoma',
    searchable=False
)

CCAAEvolutionGraph = dcc.Graph(
        id='CCAAEvolutionGraph',
        config = {'modeBarButtonsToRemove': ['pan2d','zoom2d','zoomIn2d','zoomOut2d','hoverClosestCartesian','autoScale2d','resetScale2d','toggleSpikelines']}
    )

CCAAEvolutionBox_children = [CCAAEvolutionGraph,dropdownCCAA]

CCAAEvolutionBox = html.Div(
    children = CCAAEvolutionBox_children,
    className = 'col-lg-6'
)
###################################
mapWidget = dcc.Graph()
mapDropdown = dcc.Dropdown(
    options = [{'label':'1','value':'1'}],
    searchable=False
)
mapWidgetBox = html.Div(
    children = [mapWidget,mapDropdown]
)
####################################
# Grid layout for the plots widgets



###################################################################################
#
#
# IN THIS SECTION I CREATE THE APP AND ITS LAYOUT

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app_header = html.H1(
    children='Estado del brote de COVID-19 en España',
    className = 'mb-5 mt-1'
)


evolutionWidget = html.Div(
    className = 'row',
    children = [
        nationalEvolutionBox,
        CCAAEvolutionBox
    ]
)
evolutionWidgetTab = dcc.Tab(
    label = 'Evolución',
    children = evolutionWidget
)

mapWidgetTab =  dcc.Tab(
    label = 'Mapa',
    children = mapWidget
)

myTabs = dcc.Tabs([evolutionWidgetTab,mapWidgetTab])

app_children = [app_header,myTabs]
app.layout = html.Div(
    className = 'container-fluid',
    children = [
    html.Div(
        className = 'container-fluid',
        children = app_children
    )
    ]
)


###################################################################################
#
#
# IN THIS SECTION I CREATE THE COMPONENTS CALLBACKS

# Callback to plot different CCAA when selected in the Dropdown list
@app.callback(
    Output('CCAAEvolutionGraph', 'figure'),
    [Input('dropdownCCAA', 'value')])
def update_CCAA_figure(CCAA_name):
    df = communities_data_frames_dict[CCAA_name]

    CCAAEvolutionFig = go.Figure(
        layout = go.Layout(
            legend=dict(
                x=0,
                y=1
            ),
            xaxis =  {
                'showgrid': False
            },
            yaxis =  {
                'showgrid': False
            },
            title="Comunidades autónomas",
            yaxis_title="Casos",
            xaxis_title=""
        )
    )
    CCAAEvolutionFig.add_trace(
        go.Scatter(
            x=df[date_column_name], y=df[activeCases_column_name],
            mode='none',
            name = activeCases_column_name,
            stackgroup='one' # define stack group
        )
    )
    CCAAEvolutionFig.add_trace(
        go.Scatter(
            x=df[date_column_name], y=df[deaths_column_name],
            mode='none',
            name = deaths_column_name,
            stackgroup='one' # define stack group
        )
    )
    CCAAEvolutionFig.add_trace(
        go.Scatter(
            x=df[date_column_name], y=df[recovered_column_name],
            mode='none',
            name = recovered_column_name,
            stackgroup='one' # define stack group
        )
    )

    return CCAAEvolutionFig



if __name__ == '__main__':
    app.run_server(debug=True)
