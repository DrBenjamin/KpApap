import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import math
from datetime import datetime
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
# Perform query
def run_query(query):
  with conn.cursor() as cur:  
    cur.execute(query)
    return cur.fetchall()

## Title and some information
# Ask for language (whole site)
lang = st.selectbox('In which language should this site appear?', ('BG', 'CS', 'DA', 'DE', 'EL', 'EN-GB', 'ES', 'ET', 'FI', 'FR', 'HU', 'IT', 'JA', 'LT', 'LV', 'NL', 'PL', 'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'ZH'), index = 5, key = 'lang')
title = 'GEOMAGNETIC ACTIVITY'
subheader = 'Planetary indicators of geomantic activity'
info1 = 'The geomagnetic 3-hour Kp index was introduced in 1949 by J. Bartels and is calculated from the standardized K indices (Ks) of 13 geomagnetic observatories. It was developed to measure solar particle radiation via its magnetic effects and is now considered a proxy for the energy input from the solar wind into the Earth system.'
info2 = 'Because of the non-linear relationship of the K-scale to magnetometer fluctuations, it is not meaningful to take the average of a set of K-indices. Instead, every 3-hour K-value will be converted back into a linear scale called the a-index or just ap.'
if lang != 'EN-GB' :
  title = trans(title, lang)
  info1 = trans(info1, lang)
  info2 = trans(info2, lang)
  subheader = trans(subheader, lang)
st.title(title)
st.subheader(subheader)
st.write(str(info1))
st.write(str(info2))

# Link to data from Helmholtz-Zentrum Potsdam
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt
DATA_URL = 'https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt'

## Load data function
# Function is cached
@st.cache
def load_data():
  colnames = ['Year', 'Month', 'Day', 'Hour', 'Hour_m', 'Days', 'Days_m', 'Kp', 'ap', 'D']
  data = pd.read_table(DATA_URL, sep = " ", header = None, names = colnames, skiprows = 31, skipinitialspace = True)
  return data

# Show loading message
data_load_text = 'Loading data...'
data_down_text = 'Data downloaded'
if lang != 'EN-GB' :
  data_load_text = trans(data_load_text, lang)
  data_down_text = trans(data_down_text, lang)
data_load_state = st.text(data_load_text)
data = load_data()
data_load_state.text(str(data_down_text) + ' (' + str(round(sys.getsizeof(data)/1048576, 2)) + 'MB)!')

## Checkbox for option to see raw data
check1 = 'Show raw data?'
if lang != 'EN-GB' :
  check1 = trans(check1, lang)
if st.checkbox(str(check1)):
  check1sub = 'Raw data'
  if lang != 'EN-GB' :
    check1sub = trans(check1sub, lang)
  st.subheader(check1sub)
  st.write(data)
# Create data frames
data_plot_today = pd.DataFrame({'Time': data.Hour.astype(int), 'Kp': data.Kp}).tail(8)
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
        # Creating top 10 list
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
# Create dataframe with avg ap per day values
data_plot = pd.DataFrame({'Date': pd.to_datetime(avg_ap_d_t),
                         'ap': avg_ap_d})
                         
## Plotting
# Set indexes (x-axis) to 'Time' and 'Date' column
data_plot_today = data_plot_today.set_index('Time')
data_plot = data_plot.set_index('Date')
# Daily activity
plot1_subheader = 'Diagram of today`s geomagnetic activity (Kp)'
plot2_subheader = 'Diagram of geomagnetic activity since 1932 (ap)'
if lang != 'EN-GB' :
  plot1_subheader = trans(plot1_subheader, lang)
  plot2_subheader = trans(plot2_subheader, lang)
st. subheader(plot1_subheader)
st.bar_chart(data_plot_today)
# All data plot
st.subheader(plot2_subheader)
st.line_chart(data_plot)

## Show 10 maximum ap days
list.sort(max_ap, reverse = True)
max_ap_data = pd.DataFrame()
max_ap_data['Date'] = [sublist[1] for sublist in max_ap]
max_ap_data['ap'] = [sublist[0] for sublist in max_ap]
max_ap_data_index = pd.Index(range(1, 11, 1))
max_ap_data = max_ap_data.set_index(max_ap_data_index)
# Show top 10 data
info_maxap = 'The maximum of the daily average ap was on '
info_maxapat = 'at'
if lang != 'EN-GB' :
  info_maxap = trans(info_maxap, lang)
  info_maxapat = trans(info_maxapat, lang)
st.write(str(info_maxap), str(max_ap[0][1]), ' ', str(info_maxapat), ' ', str(max_ap[0][0]), '.')
check_maxap = 'Show maximum days?'
check_maxapsubheader = 'Top 10'
if lang != 'EN-GB' :
  check_maxap = trans(check_maxap, lang)
  check_maxapsubheader = trans(check_maxapsubheader, lang)
if st.checkbox(str(check_maxap)):
  st.subheader(check_maxapsubheader)
  st.write(max_ap_data)
  
## Use local databank
use_databank = 'Use local databank?'
if lang != 'EN-GB' :
  use_databank = trans(use_databank, lang)
if st.checkbox(str(use_databank)):
  conn = init_connection()
  # Ask for events
  day_event = 'On which day was the event?'
  text_input = 'What happened on this day?'
  text_output = 'You selected'
  text_placeholder = 'All kinds of events'
  if lang != 'EN-GB' :
    day_event = trans(day_event, lang)
    text_input = trans(text_input, lang)
    text_output = trans(text_output, lang)
    text_placeholder = trans(text_placeholder, lang)
  date = st.selectbox(str(day_event), max_ap_data, key = 'date')
  st.write(str(text_output), date)
  event = st.text_input(str(text_input), placeholder = text_placeholder, key = 'event')
  # Write data to databank
  stored_data = 'Store in databank?'
  stored_datasuccess = 'stored to databank!'
  show_data = 'Show databank data?'
  show_datasubheader = 'Databank data'
  if lang != 'EN-GB' :
    stored_data = trans(stored_data, lang)
    stored_datasuccess = trans(stored_datasuccess, lang)
    show_data = trans(show_data, lang)
    show_datasubheader = trans(show_datasubheader, lang)
  if st.button(str(stored_data)):
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
    st.write(date, event, ' ', stored_datasuccess)
  # Checkbox for option to see databank data
  if st.checkbox(str(show_data)):
    st.subheader(show_datasubheader)
    query = "SELECT * from `dbs5069306`.`topten`;"
    rows = run_query(query)
    databank = pd.DataFrame(columns = ['ID', 'Date', 'Event'])
    for row in rows:
      df = pd.DataFrame([[row[0], row[1], row[2]]], columns = ['ID', 'Date', 'Event'])
      databank = databank.append(df)
    # Print databank in dataframe table
    databank = databank.set_index('ID')
    st.table(databank)
