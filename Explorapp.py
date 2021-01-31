import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pydeck as pdk
from PIL import Image

#Load Image
image = Image.open('header.jpg')
st.image(image, use_column_width=True)

#Opens MapBox Token
mapbox_access_token = open("mapbox").read()

#st.set_page_config(layout="wide")

'''
# Exploration Data App
This is a Streamlit App deployed on a local K3s cluster that presents data from Alberta Energy Regulator (AER)
Well Licences (ST1) and Well Spud Data (ST49) which are updated daily. AER publishes this data in Text format. 

## Data Flow
Server currently runs a script daily to download the text files, parses them into dataframes, creates csv files and commits the changes
to the repository, which triggers a container update to rebuild the **latest** image, which then is pulled by the K3s cluster
'''

#ST49 data
ST49_2020 = pd.read_csv('ST49-2020.csv')
ST49_2020.rename(columns={'Lat': 'lat', 'Long': 'lon'}, inplace=True)

ST49_2021 = pd.read_csv('ST49-2021.csv')
ST49_2021.rename(columns={'Lat': 'lat', 'Long': 'lon'}, inplace=True)

ST49 = pd.concat([ST49_2020, ST49_2021])

#ST1 Data
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

#Bar Chart Year Comparison
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
fig1.update_layout(barmode='group', xaxis_title="Week", yaxis_title="Count", legend_title="Year")

st.plotly_chart(fig1)

#Bar Chart Substance Count per Week
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

fig.update_layout(barmode='group', xaxis_title="Week", yaxis_title="Count", legend_title="Substance")

st.plotly_chart(fig)

#Location for Well Licences
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

fig2 = go.Figure(go.Scattermapbox(
        lat=filter_data['lat'],
        lon=filter_data['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=filter_data['SUBSTANCE'],
    ))

fig2.update_layout(
    height = 600,
    width = 700,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=midpoint[0],
            lon=midpoint[1]
        ),
        pitch=0,
        zoom=3,
        style='dark'
    )
)
st.plotly_chart(fig2)

#Dataframe of selected Operator
'''
## Data for selected Operator

'''
#Dataframe showing filtered data from selected Licensee
st.dataframe(filter_data.sort_values(by='WEEK'))

#ST49 Year Comparison
'''
---
---
## Well Spuds per Week (2020 vs 2021)
Spuds for all operators and all substances
'''
week_year49 = ST49

#Bar Chart
week_year49 = pd.pivot_table(week_year49, index=['WEEK'], columns=['YEAR'], values=['LICENSEE'], aggfunc='count')
week_year49.columns = week_year49.columns.droplevel(0)
week_year49 = week_year49.rename_axis(None, axis=1)
week_year49 = week_year49.reset_index().drop('index', axis=1, errors='ignore')
week_year49.fillna(0, inplace=True)
week_year49.drop(week_year49.tail(1).index,inplace=True)

fig49 = go.Figure(data=[
    go.Bar(name='2020', x=week_year49['WEEK'], y=week_year49[2020]),
    go.Bar(name='2021', x=week_year49['WEEK'], y=week_year49[2021])
])
fig49.update_layout(barmode='group', xaxis_title="Week", yaxis_title="Count", legend_title="Year")

st.plotly_chart(fig49)

#ST49 Locations
'''
## Well Spuds Locations by Operator (2021 YTD)

'''
#Create Dropdown by Licensee
licensee49 = list(ST49_2021.LICENSEE.unique())
option49 = st.selectbox('Select Operator from the list below to update locations', sorted(licensee49))
filter_data49 = ST49_2021[ST49_2021['LICENSEE'] == option49]

#Map from selected Licensee
#st.map(filter_data49)
midpoint49 = (np.average(ST49_2021['lat']), np.average(ST49_2021['lon']))


fig49_2 = go.Figure(go.Scattermapbox(
        lat=filter_data49['lat'],
        lon=filter_data49['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=filter_data49['CONTRACTOR NAME'],
    ))

fig49_2.update_layout(
    height = 600,
    width = 700,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=midpoint49[0],
            lon=midpoint49[1]
        ),
        pitch=0,
        zoom=3,
        style='dark'
    )
)
st.plotly_chart(fig49_2)

'''
## Data for selected Operator

'''
#Dataframe showing filtered data from selected Licensee
st.dataframe(filter_data49.sort_values(by='WEEK'))
