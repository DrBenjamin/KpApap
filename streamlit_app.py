import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

st.title('GEOMAGNETIC ACTIVITY')
st.subheader('Planetary indicators of geomantic activity')
st.write('The geomagnetic 3-hour Kp index was introduced in 1949 by J. Bartels and is calculated from the standardized K indices (Ks) of 13 geomagnetic observatories. It was developed to measure solar particle radiation via its magnetic effects and is now considered a proxy for the energy input from the solar wind into the Earth system.')

DATE_COLUMN = 'date/time'
# Link to Helmholtz-Zentrum Potsdam
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt
# https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt
# CSV Testfile: https://www.benbox.org/R/py/test.csv
# Text Testfile: https://www.benbox.org/R/py/test.txt
DATA_URL = ('https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt')

@st.cache
def load_data():
    colnames = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Days', 'Days_m', 'Kp', 'ap', 'D']
    data = pd.read_table(DATA_URL, sep = " ", header = None, names = colnames, skiprows = 31, skipinitialspace = True)
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("Kp und ap downloaded!")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Diagram of geomagnetic activity')
data_plot = pd.DataFrame({"Year":data.Year,
                          "ap":data.ap})
st.line_chart(data_plot)
st.altair_chart(data_plot)
