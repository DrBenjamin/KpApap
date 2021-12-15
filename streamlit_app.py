import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import math
import datetime

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

## create a data frame
data_cal = pd.DataFrame({"Year":pd.to_datetime(data.Year.map(str) + "-" + data.Month.map(str) + "-" + data.Day.map(str)),
                          "ap":data.ap})

# avg ap per day as a string list for args
test_str = ""
avg_ap_d = []
avg_ap_d_t = []
x = 0
max_ap = 0
for i in range(1, len(data_cal)) : 
  if data_cal['Year'][i] == test_str or i == 1:
    x = x + data_cal['ap'][i]
    test_str = data_cal['Year'][i]
  else :
    x = x / 8
    avg_ap_d_t.append(str(data_cal['Year'][i]))
    avg_ap_d.append(int(np.ceil(x)))
    if x > max_ap :
      max_ap = np.ceil(x)
      max_ap_y = str(data_cal['Year'][i])
    x = 0
    x = data_cal['ap'][i]
    test_str = data_cal['Year'][i]

max_ap_y = max_ap_y[0:10]  
st.write('The maximum of the daily average ap was ', str(max_ap), ' on ', str(max_ap_y))

## Plotting
st.subheader('Diagram of geomagnetic activity')
# create dataframe with avg ap per day values
data_plot = pd.DataFrame({'Year': pd.to_datetime(avg_ap_d_t),
                         'ap': avg_ap_d})
# set index (x-axis) to 'Year' column
data_plot = data_plot.set_index('Year')
# do the plotting
st.line_chart(data_plot)
