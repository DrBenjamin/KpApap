import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import math
import datetime
#import mysql.connector

st.set_page_config(
     page_title = "KpApap",
     page_icon = "thumbnail.png",
     #layout = "wide",
     initial_sidebar_state = "expanded",
)

## SQL Connection
# Initialize connection.
# Uses st.cache to only run once.
#def init_connection():
#    return mysql.connector.connect(**st.secrets["mysql"])

#conn = init_connection()

# Perform query.
# Uses st.cache to only rerun when the query changes or after 10 min.
#@st.cache(ttl=600)
#def run_query(query):
#    with conn.cursor() as cur:
#        cur.execute(query)
#        return cur.fetchall()

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
@st.cache
def load_data():
    colnames = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Days', 'Days_m', 'Kp', 'ap', 'D']
    data = pd.read_table(DATA_URL, sep = " ", header = None, names = colnames, skiprows = 31, skipinitialspace = True)
    return data

# Show loading message
data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('ap data downloaded!')

## Checkbox for option to see raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
# create a data frame
data_cal = pd.DataFrame({'Date':pd.to_datetime(data.Year.map(str) + "-" + data.Month.map(str) + "-" + data.Day.map(str)),
                          'ap':data.ap})

## calculation of avg ap per day and top 10 max values
# Function which is cachable
@st.cache
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
st.subheader('Diagram of geomagnetic activity')
# set index (x-axis) to 'Date' column
data_plot = data_plot.set_index('Date')
# do the plotting
st.line_chart(data_plot)

## Show 10 maximum ap days
max_ap_data = pd.DataFrame()
max_ap_data['Date'] = [sublist[1] for sublist in max_ap]
max_ap_data['ap'] = [sublist[0] for sublist in max_ap]
max_ap_data_index = pd.Index(range(1, 11, 1))
max_ap_data = max_ap_data.set_index(max_ap_data_index)
# Show top 10 data                    
#st.write('The maximum of the daily average ap was ', str(int(max_ap[0])), ' on ', str(max_ap_y[0]), '.')
if st.checkbox('Show max. ap days'):
    st.subheader('Top 10 max. ap')
    st.write(max_ap_data)
    # Ask for events
#date = st.selectbox('On which day was the event?', max_ap_data)
#st.write('You selected:', date)
#event = st.text_input('What happened on this day?', placeholder = 'All kinds of events')
# # write to databank
# if st.button('Store in databank?'):
#   # Check for ID number
#   id = 0
#   query = "SELECT ID from `dbs5069306`.`topten`;"
#   rows = run_query(query)
#   row = [0]
#   for row in rows:
#     # checking for ID
#     print(row[0])
#   id = int(row[0]) + 1
#   # write to databank
#   query = "INSERT INTO `dbs5069306`.`topten` VALUES ('%s', '%s', '%s');" %(id, date, event)
#   run_query(query)
#   conn.commit()
#   st.write(date, event, ' stored to databank!')
# # Checkbox for option to see databank data
# if st.checkbox('Show databank data'):
#   st.subheader('Databank data')
#   query = "SELECT * from `dbs5069306`.`topten`;"
#   rows = run_query(query)
#   databank = pd.DataFrame(columns = ['ID', 'Date', 'Event'])
#   for row in rows:
#     df = pd.DataFrame([[row[0], row[1], row[2]]],
#     columns = ['ID', 'Date', 'Event'])
#     databank = databank.append(df)
#   # print databank in dataframe table
#   databank = databank.set_index('ID')
#   st.dataframe(databank)
