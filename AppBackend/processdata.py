# Import Built in modules
from urllib.request import urlretrieve # retrieve files from urls
import os # operative system utilities
import re # regular expressions

# Third party modules
import pandas as pd
import geopandas as gpd
import numpy as np

# The codes for the autonomous comunities (CCAA) in the dataframe use the ISO convention
# 'ISO 3166-2:ES' : https://www.iso.org/obp/ui/es/#iso:code:3166:ES.
# I make a mapping from the names of the CCAA to the ISO codes with a dictionary
def make_CCAA_dict():
    communities ="""
    ES-AN,Andalucía
    ES-AR,Aragón
    ES-AS,Asturias
    ES-CN,Canarias
    ES-CB,Cantabria
    ES-CM,Castilla La Mancha
    ES-CL,Castilla y León
    ES-CT,Catalunya
    ES-EX,Extremadura
    ES-GA,Galiza
    ES-IB,Illes Balears
    ES-RI,La Rioja
    ES-MD,Madrid
    ES-MC,Murcia
    ES-NC,Navarra
    ES-PV,Euskadi
    ES-VC,Comunitat Valenciana
    ES-CE,Ceuta
    ES-ML,Melilla
    """
    # Dictionary relating "CCA names":"ISO CODES"
    CCAA_dict = {}
    for line in communities.strip().split('\n'):
        code,name = line.strip().split(',')
        code = code.replace('ES-','')
        CCAA_dict[name] = CCAA_dict.get(name,code)
    return CCAA_dict

# The CCAA are encoded with cartographic IDS from 1 to 19 in the geodata_frame.
# Make a dictionary to translate them into CCAA ISO codes.
def make_CCAA_cartodb_ID_dict():
    cartodb_ID_str ="""
    ES-AN,16
    ES-AR,15
    ES-AS,14
    ES-CN,19
    ES-CB,12
    ES-CM,10
    ES-CL,11
    ES-CT,9
    ES-EX,7
    ES-GA,6
    ES-IB,13
    ES-RI,17
    ES-MD,5
    ES-MC,4
    ES-NC,3
    ES-PV,2
    ES-VC,8
    ES-CE,18
    ES-ML,1
    """
    # Dictionary relating "cartographic ID numbers":"ISO CODES"
    CCAA_cartodb_ID_dict = {}
    for line in cartodb_ID_str.strip().split('\n'):
        code,ID = line.strip().split(',')
        ID = int(ID)
        code = code.replace('ES-','')
        CCAA_cartodb_ID_dict[ID] = CCAA_cartodb_ID_dict.get(ID,code)
    return CCAA_cartodb_ID_dict

# Function to download the csv data file from the webpage of the health ministry in
# the correct encoding and removing unwanted symbols in the data rows like '*'
def downloadDATA(data_url, data_file_name = 'data.csv'):
    """"
    Function to download the csv data file from the webpage of the health ministry in
    the correct encoding and removing unwanted symbols in the data rows like '*'

    args:

    - "data_url" : URL to the csv file as string.
    - "data_file_name": name of the downloaded csv file as string

    returns a file handle.
    """
    data_file_unprocessed_name = data_url.split('/')[-1]
    path, HTTP_Message = urlretrieve(data_url,data_file_unprocessed_name);
    # The original csv file is encoded in 'iso-8859-1' and has some
    # '*' symbols for foot notes. Write a new csv file with 'utf-8'
    # encoding and remove the '*' symbols.
    unwanted = r'[*]' #regex string with the set of unwanted characters.
    with open(data_file_unprocessed_name,'r',encoding='iso-8859-1') as f_in, open(data_file_name,'w') as f_out:
        for line in f_in:
            f_out.write( re.sub(unwanted,'',line) ) #regex substitution of unwanted characters
        os.remove(data_file_unprocessed_name) #Removed unprocessed data csv file
        return f_out


# Function to make a data frame for the national data from the csv file
def makeNationalDataFrame(data_file_name = 'data.csv'):
    # Get the names of the columns of the csv file
    data_head = list( pd.read_csv(data_file_name,nrows=0).columns )
    # Data types for the columns
    data_types = {
        data_head[0]:str,
        data_head[1]:str,
        data_head[2]:np.float64,
        data_head[3]:np.float64,
        data_head[4]:np.float64,
        data_head[5]:np.float64,
        data_head[6]:np.float64,
        data_head[7]:np.float64,
        data_head[8]:np.float64
    }
    fill_na_dict =  {
        data_head[0]:'',
        data_head[1]:'',
        data_head[2]:0.,
        data_head[3]:0.,
        data_head[4]:0.,
        data_head[5]:0.,
        data_head[6]:0.,
        data_head[7]:0.,
        data_head[8]:0.
    }
    # Load the data into a pandas data frame with the correct data types
    data = pd.read_csv(data_file_name,dtype=data_types)
    # Remove Unnamed columns:
    unnamed_cols_iterator = filter(lambda column: 'Unnamed:' in column ,data_head )
    for col in unnamed_cols_iterator:
        data.pop(col);
    # Substitute the NA values with 0s
    data.fillna(fill_na_dict,inplace=True)
    # strip tailing whitespaces in the column names
    data.rename(columns=lambda name : name.strip(),inplace=True)
    # Put the dates in the YYYY-MM-DD format and datetime64 type
    data[data.columns[1]] = pd.to_datetime(data[data.columns[1]],format='%d/%m/%Y',errors='coerce')
    # remove the rows with no date values
    data.dropna(inplace=True,subset=[data.columns[1]])
    # sort the rows by date value
    data.sort_values(by=[data.columns[1]],ignore_index=True,inplace=True)
    # return the data frame
    return data


# Function to create a dictionary with a dataframe for every CCAA.
# The key is the CCAA name
def makeCommunitiesDataFrameDict(national_data_frame):
    CCAA_label = national_data_frame.columns[0]
    communities_data_frames_dict = dict()
    CCAA_dict = make_CCAA_dict()
    for name,code in CCAA_dict.items():
        df = national_data_frame[national_data_frame[CCAA_label]==code]
        df.reset_index(drop=True,inplace=True)
        communities_data_frames_dict[name] = df
    return communities_data_frames_dict
