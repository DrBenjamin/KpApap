import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import math
import datetime
import mysql.connector
import deepl
import sys

def trans(x, y):
  translator = deepl.Translator(st.secrets["deepl"]["key"])
  result = translator.translate_text(x, target_lang = y) 
  return result

st.set_page_config(
  page_title = "KpApap",
  page_icon = "thumbnail.png",
  #layout = "wide",
  initial_sidebar_state = "expanded",
)

## SQL Connection
# Initialize connection.
def init_connection():
  return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query
def run_query(query):
  with conn.cursor() as cur:  
    cur.execute(query)
    return cur.fetchall()

## Title and some information
st.title('GEOMAGNETIC ACTIVITY')
st.subheader('Planetary indicators of geomantic activity')
st.write('The geomagnetic 3-hour Kp index was introduced in 1949 by J. Bartels and is calculated from the standardized K indices (Ks) of 13 geomagnetic observatories. It was developed to measure solar particle radiation via its magnetic effects and is now considered a proxy for the energy input from the solar wind into the Earth system.')
st.write('Because of the non-linear relationship of the K-scale to magnetometer fluctuations, it is not meaningful to take the average of a set of K-indices. Instead, every 3-hour K-value will be converted back into a linear scale called the a-index or just ap.')

# Link to data from Helmholtz-Zentrum Potsdam
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt
DATA_URL = 'https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt'

## Load data function
# Function is cached
@st.cache
def load_data():
  colnames = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Days', 'Days_m', 'Kp', 'ap', 'D']
  data = pd.read_table(DATA_URL, sep = " ", header = None, names = colnames, skiprows = 31, skipinitialspace = True)
  return data

# Show loading message
data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Data downloaded (' + str(round(sys.getsizeof(data)/1048576, 2)) + 'MB)!')

## Checkbox for option to see raw data
if st.checkbox('Show raw data'):
  st.subheader('Raw data')
  st.write(data)
# Create a data frames
data_plot_td = pd.DataFrame({'Time': data.Hour, 'ap': data.ap}).tail(8)
data_cal = pd.DataFrame({'Date': pd.to_datetime(data.Year.map(str) + "-" + data.Month.map(str) + "-" + data.Day.map(str)), 'ap': data.ap})

## Calculation of avg ap per day and top 10 max values
# Function is cached
@st.cache(allow_output_mutation=True)
def calc_top10(date, ap):
  avg_ap_d = []
  avg_ap_d_t = []
  max_ap = [ [0, ''], [0, ''], [0, ''], [0, ''], [0, ''], [0, ''], [0, ''], [0, ''], [0, ''], [0, ''] ]
  test_str = ""
  x = 0
  for i in range(1, len(ap)) : 
    if date[i] == test_str or i == 1:
      x = x + ap[i]
      test_str = date[i]
    else :
      x = x / 8
      avg_ap_d_t.append(str(test_str))
      avg_ap_d.append(int(np.ceil(x)))
      for y in range(0, 10, 1) :
        # creating top 10 list
        if x > max_ap[y][0] :
          max_ap[y][0] = int(np.ceil(x))
          max_ap[y][1] = str(test_str)[0:10]
          list.sort(max_ap, reverse = False)
          break
      x = ap[i]
      test_str = date[i]
  return avg_ap_d, avg_ap_d_t, max_ap
# Call function to do the calculation
avg_ap_d, avg_ap_d_t, max_ap = calc_top10(date = data_cal['Date'], ap = data_cal['ap'])
# create dataframe with avg ap per day values
data_plot = pd.DataFrame({'Date': pd.to_datetime(avg_ap_d_t),
                         'ap': avg_ap_d})
                         
## Plotting
# Set indexes (x-axis) to 'Date' column
data_plot_td = data_plot_td.set_index('Time')
data_plot = data_plot.set_index('Date')
# Daily activity
st. subheader('Diagram of today`s geomagnetic activity')
st.bar_chart(data_plot_td)
# All data plot
st.subheader('Diagram of geomagnetic activity since 1932')
st.line_chart(data_plot)

## Show 10 maximum ap days
list.sort(max_ap, reverse = True)
max_ap_data = pd.DataFrame()
max_ap_data['Date'] = [sublist[1] for sublist in max_ap]
max_ap_data['ap'] = [sublist[0] for sublist in max_ap]
max_ap_data_index = pd.Index(range(1, 11, 1))
max_ap_data = max_ap_data.set_index(max_ap_data_index)
# Show top 10 data                    
st.write('The maximum of the daily average ap was on ', str(max_ap[0][1]), ' at ', str(max_ap[0][0]), '.')
if st.checkbox('Show max. ap days'):
  st.subheader('Top 10 max. ap')
  st.write(max_ap_data)
# Ask for events
date = st.selectbox('On which day was the event?', max_ap_data, key = 'date')
st.write('You selected:', date)
event = st.text_input('What happened on this day?', placeholder = 'All kinds of events', key = 'event')
# Write data to databank
if st.button('Store in databank?'):
# Check for ID number
  id = 0
  query = "SELECT ID from `dbs5069306`.`topten`;"
  rows = run_query(query)
  row = [0]
  for row in rows:
    # Checking for ID
    print(row[0])
    id = int(row[0]) + 1
  # Writing to databank
  query = "INSERT INTO `dbs5069306`.`topten` VALUES ('%s', '%s', '%s');" %(id, date, event)
  run_query(query)
  conn.commit()
  st.write(date, event, ' stored to databank!')
# Checkbox for option to see databank data
if st.checkbox('Show databank data'):
  st.subheader('Databank data')
  query = "SELECT * from `dbs5069306`.`topten`;"
  rows = run_query(query)
  lang = st.selectbox('In which language should the event text be translated?', ('BG', 'CS', 'DA', 'DE', 'EL', 'EN-GB', 'ES', 'ET', 'FI', 'FR', 'HU', 'IT', 'JA', 'LT', 'LV', 'NL', 'PL', 'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'ZH'), index = 3, key = 'lang')
  databank = pd.DataFrame(columns = ['ID', 'Date', 'Event'])
  for row in rows:
    if lang != 'EN-GB' :
      trans_event = str((trans(row[2], lang)))
    else:
      trans_event = row[2]
    df = pd.DataFrame([[row[0], row[1], trans_event]], columns = ['ID', 'Date', 'Event'])
    databank = databank.append(df)
  # Print databank in dataframe table
  databank = databank.set_index('ID')
  #st.dataframe(databank, 400, 200)
  st.table(databank)
