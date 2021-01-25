import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

'''
# Exploration Data App
This is a Streamlit App deployed on a local K3s cluster that presents data from Alberta Energy Regulator (AER)
Well Licences (ST1) and Well Spud Data (ST49) which are updated daily. AER publishes this data in Text format. 

## Data Flow
Server currently runs a script daily to download the text files, parses them into dataframes, creates csv files and commits the changes
to the repository, which triggers a container update to rebuild the **latest** image, which then is pulled by the K3s cluster
'''

#Open ST1 data
ST1 = pd.read_csv('ST1.csv')
ST49 = pd.read_csv('ST49.csv')

'''
## Well Licences Issued by Week (2020 vs 2021)
Licences issued for all operators and all substances
'''
week_year = ST1

#Bar Chart
week_year = pd.pivot_table(week_year, index=['WEEK'], columns=['YEAR'], values=['LICENSEE'], aggfunc='count')
week_year.columns = week_year.columns.droplevel(0)
week_year = week_year.rename_axis(None, axis=1)
week_year = week_year.reset_index().drop('index', axis=1, errors='ignore')
week_year.fillna(0, inplace=True)

chart=[]
fig1 = go.Figure(data=[
    go.Bar(name='2020', x=week_year['WEEK'], y=week_year[2020]),
    go.Bar(name='2021', x=week_year['WEEK'], y=week_year[2021])
])
# Change the bar mode
fig1.update_layout(barmode='group')

st.plotly_chart(fig1)

'''
## Weekly Activity (2020)

Licenses issued by week broken down by substance (for all operators)
'''
df = ST1[ST1['YEAR'] == 2020]

#Data Cleaning for Weekly Data
df = pd.pivot_table(df, index=['WEEK'], columns=['SUBSTANCE'], values=['LICENSEE'], aggfunc='count')
df.columns = df.columns.droplevel(0)
df = df.rename_axis(None, axis=1)
if isinstance(df, (pd.DatetimeIndex, pd.MultiIndex)):
	df = df.to_frame(index=False)

#Remove any pre-existing indices for ease of use in the D-Tale code, but this is not required
df = df.reset_index().drop('index', axis=1, errors='ignore')
df.columns = [str(c) for c in df.columns]  # update columns to strings in case they are numbers

chart_data = pd.concat([
	df['WEEK'],
	df['CRUDE OIL'],
	df['CRUDE BITUMEN'],
	df['GAS'],
], axis=1)
chart_data = chart_data.sort_values(['WEEK'])
chart_data = chart_data.rename(columns={'WEEK': 'x'})
chart_data = chart_data.dropna()

#Plotly Graph

fig = go.Figure()
fig.add_trace(go.Scatter(x=chart_data['x'], y=chart_data['CRUDE OIL'],
                    mode='lines',
                    name='Crude Oil'))
fig.add_trace(go.Scatter(x=chart_data['x'], y=chart_data['GAS'],
                    mode='lines',
                    name='Gas'))
fig.add_trace(go.Scatter(x=chart_data['x'], y=chart_data['CRUDE BITUMEN'],
                    mode='lines', name='Crude Bitumen'))

st.plotly_chart(fig)


'''
## AER ST1 Well Licences Locations by Operator

Note: Zoom out to see all locations for the selected operator
'''
#Create Dropdown by Licensee
licensee = ST1.LICENSEE.unique()
option = st.selectbox('Select Operator from the list below to update locations', sorted(licensee))
filter_data = ST1[ST1['LICENSEE'] == option]

#Map from selected Licensee
st.map(filter_data)
'''
## Data for selected Operator

'''
#Dataframe showing filtered data from selected Licensee
st.dataframe(filter_data.sort_values(by='WEEK'))
