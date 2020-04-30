# Import Built in modules
import json # JSON files utilities
from urllib.request import urlretrieve # retrieve files from urls
import os # operative system utilities
import re # regular expressions

# pandas and geopandas
import pandas as pd
import geopandas as gpd

#numpy
import numpy as np

#dash, to build the app
import dash
import dash_core_components as dcc
import dash_html_components as html

# Import my backend module
from AppBackend import processdata

#               THIS SECTION OF THE MODULE DOWNLOADS THE DATA AND PROCESS IT INTO DATAFRAMES
# Tuples to store the names and codes of the CCAA
CCAA_dict = processdata.make_CCAA_dict()
CCAA_names_tuple = tuple( sorted(CCAA_dict.keys()) )
CCAA_codes_tuple = tuple( sorted(CCAA_dict.values()) )

# Dictionary relating "cartographic ID numbers":"ISO CODES"
CCAA_cartodb_ID_dict = processdata.make_CCAA_cartodb_ID_dict()


#                Script to obtain COVID data in SPAIN
#
# - data_COVID19_spain = data frame with all the data for spain
# - data_COVID19_spain_last = data frame with the last update
# - commcommunities_data_frames_dict = dictionary containing data frames for
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
data_COVID19_spain[cases_column_name] += data_COVID19_spain[PCR_column_name]

# Make a column for the ACTIVE cases
data_COVID19_spain[activeCases_column_name] = data_COVID19_spain[cases_column_name] - data_COVID19_spain[deaths_column_name] - data_COVID19_spain[recovered_column_name]


#App


external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app_header = html.H1(children='Estado actual de COVID-19')



########################################
nationalEvolutionGraph = dcc.Graph()

nationalEvolutionBox_children = [nationalEvolutionGraph]
nationalEvolutionBox = html.Div(
    children = nationalEvolutionBox_children,
    className = 'col-md-6'
)

#########################################



dropdownCCAA = dcc.Dropdown(
    options = [{'label':CCAA,'value':CCAA} for CCAA in CCAA_names_tuple],
    placeholder = 'Comunidad autónoma',
    searchable=False
)
CCAAEvolutionWidget = dcc.Graph()

CCAAEvolutionBox_children = [dropdownCCAA,CCAAEvolutionWidget]

CCAAEvolutionBox = html.Div(
    children = CCAAEvolutionBox_children,
    className = 'col-md-6'
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

if __name__ == '__main__':
    app.run_server(debug=True)
