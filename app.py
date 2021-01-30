import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pydeck as pdk

#st.set_page_config(layout="wide")
'''
# Exploration Data App
This is a Streamlit App deployed on a local K3s cluster that presents data from Alberta Energy Regulator (AER)
Well Licences (ST1) and Well Spud Data (ST49) which are updated daily. AER publishes this data in Text format. 

## Data Flow
Server currently runs a script daily to download the text files, parses them into dataframes, creates csv files and commits the changes
to the repository, which triggers a container update to rebuild the **latest** image, which then is pulled by the K3s cluster
'''

#Open data
ST49 = pd.read_csv('ST49.csv')
ST1_2020 = pd.read_csv('ST1-2020.csv')
ST1_2020.rename(columns={'Lat': 'lat', 'Long': 'lon'}, inplace=True)
ST1_2021 = pd.read_csv('ST1-2021.csv')
ST1_2021.rename(columns={'Lat': 'lat', 'Long': 'lon'}, inplace=True)
ST1 = pd.concat([ST1_2020, ST1_2021])

'''
## Well Licences Issued per Week (2020 vs 2021)
Licences issued for all operators and all substances
'''
week_year = ST1

#Bar Chart
week_year = pd.pivot_table(week_year, index=['WEEK'], columns=['YEAR'], values=['LICENSEE'], aggfunc='count')
week_year.columns = week_year.columns.droplevel(0)
week_year = week_year.rename_axis(None, axis=1)
week_year = week_year.reset_index().drop('index', axis=1, errors='ignore')
week_year.fillna(0, inplace=True)
week_year.drop(week_year.tail(1).index,inplace=True)

fig1 = go.Figure(data=[
    go.Bar(name='2020', x=week_year['WEEK'], y=week_year[2020]),
    go.Bar(name='2021', x=week_year['WEEK'], y=week_year[2021])
])
fig1.update_layout(barmode='group')

st.plotly_chart(fig1)

'''
## Well Licences by Substance per Week (2021 YTD)

'''
week_subs = ST1_2021

week_subs = pd.pivot_table(week_subs, index=['WEEK'], columns=['SUBSTANCE'], values=['LICENSEE'], aggfunc='count')
week_subs.columns = week_subs.columns.droplevel(0)
week_subs = week_subs.rename_axis(None, axis=1)
week_subs = week_subs.reset_index().drop('index', axis=1, errors='ignore')
week_subs.fillna(0, inplace=True)
week_subs.drop(week_subs.tail(1).index,inplace=True)

fig = go.Figure(data=[
    go.Bar(name='CRUDE BITUMEN', x=week_subs['WEEK'], y=week_subs['CRUDE BITUMEN']),
    go.Bar(name='CRUDE OIL', x=week_subs['WEEK'], y=week_subs['CRUDE OIL']),
    go.Bar(name='GAS', x=week_subs['WEEK'], y=week_subs['GAS'])
])

fig.update_layout(barmode='group')

st.plotly_chart(fig)

'''
## Well Licences Locations by Operator (2021 YTD)

'''
#Create Dropdown by Licensee
licensee = list(ST1_2021.LICENSEE.unique())
option = st.selectbox('Select Operator from the list below to update locations', sorted(licensee))
filter_data = ST1_2021[ST1_2021['LICENSEE'] == option]

#Map from selected Licensee
#st.map(filter_data)
midpoint = (np.average(ST1_2021['lat']), np.average(ST1_2021['lon']))

st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/dark-v9',
     initial_view_state=pdk.ViewState(
         latitude=midpoint[0],
         longitude=midpoint[1],
         zoom=4,                  
     ),
     layers=[         
         pdk.Layer(
             'ScatterplotLayer',
             data=filter_data,
             get_position='[lon, lat]',
             get_color='[200, 30, 0, 160]',
             get_radius=10000,
         ),
     ],
))

'''
## Data for selected Operator

'''
#Dataframe showing filtered data from selected Licensee
st.dataframe(filter_data.sort_values(by='WEEK'))

