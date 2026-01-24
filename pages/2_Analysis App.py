# Import necessary libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import  ast


# Set Streamlit page configuration
st.set_page_config(page_title="Analytics Page")

# Title of the web app
st.title('Analytics')

# Load data
new_df = pd.read_csv('WebPage_Development/datasets/data_viz1.csv')
wordcloud_df = pd.read_pickle(open('WebPage_Development/pickles/wordcloud_df.pkl','rb'))

# Data preprocessing for GeoMap Section
group_df = new_df.drop(columns=["property_type","society","balcony","agePossession","coordinates"]).groupby('sector').mean()[['price','price_per_sqft','built_up_area','latitude','longitude']]

# GeoMap Section
st.header('Sector Price per Sqft Geomap')
fig = px.scatter_mapbox(group_df, lat="latitude", lon="longitude", color="price_per_sqft", size='built_up_area',
                  color_continuous_scale=px.colors.cyclical.IceFire, zoom=10,
                  mapbox_style="open-street-map",width=800,height=500,hover_name=group_df.index)
st.plotly_chart(fig,use_container_width=True)

# Features Wordcloud Section
st.header('Features Wordcloud')
selected_sector_cloud = st.selectbox('Select a Sector', wordcloud_df['sector'].unique().tolist())
new_cloud = wordcloud_df[wordcloud_df['sector'] == selected_sector_cloud]
wordcloud_text = []
for item in new_cloud['features'].apply(ast.literal_eval):
    wordcloud_text.extend(item)
feature_texts = ' '.join(wordcloud_text)
wordcloud = WordCloud(width=800, height=500, background_color='black', stopwords={'s'}, min_font_size=10).generate(feature_texts)
st.image(wordcloud.to_image())

# Area Vs Price Section
st.header('Area Vs Price')
property_type = st.selectbox('Select Property Type', ['flat','house'])
if property_type == 'house':
    fig1 = px.scatter(new_df[new_df['property_type'] == 'house'], x="built_up_area", y="price", color="bedRoom", title="Area Vs Price", width=800, height=500, animation_frame='agePossession')
    st.plotly_chart(fig1, use_container_width=True)
else:
    fig1 = px.scatter(new_df[new_df['property_type'] == 'flat'], x="built_up_area", y="price", color="bedRoom",
                      title="Area VsPrice", width=800, height=500, animation_frame='agePossession')
    st.plotly_chart(fig1, use_container_width=True)

# BHK Pie Chart Section
st.header('BHK Pie Chart')
sector_options = new_df['sector'].unique().tolist()
sector_options.insert(0,'overall')
selected_sector = st.selectbox('Select Sector', sector_options)
if selected_sector == 'overall':
    fig2 = px.pie(new_df, names='bedRoom', width=800, height=500)
    st.plotly_chart(fig2, use_container_width=True)
else:
    fig2 = px.pie(new_df[new_df['sector'] == selected_sector], names='bedRoom', width=800, height=500)
    st.plotly_chart(fig2, use_container_width=True)

# Side by Side BHK Price Comparison Section
st.header('Side by Side BHK price comparison')
bedroom_df =  st.selectbox("No of bedroom",sorted(new_df["bedRoom"].unique().astype("int")),index=3)
fig3 = px.box(new_df[new_df['bedRoom'] <= bedroom_df], x='bedRoom', y='price', title='BHK Price Range', width=800, height=500)
st.plotly_chart(fig3, use_container_width=True)

# Side by Side Histogram for property type
st.header('Side by Side Distplot for property type')
hist_house = go.Histogram(x=new_df[new_df['property_type'] == 'house']['price'], nbinsx=100, name='house', opacity=0.6, marker=dict(color='blue', line=dict(color='white', width=0.5)))
hist_flat = go.Histogram(x=new_df[new_df['property_type'] == 'flat']['price'], nbinsx=100, name='flat', opacity=0.6, marker=dict(color='orange', line=dict(color='white', width=0.5)))
# Create subplot with two histograms
fig_distplot = go.Figure(data=[hist_house, hist_flat], layout=go.Layout(barmode='overlay'))
fig_distplot.update_layout(showlegend=True)
st.plotly_chart(fig_distplot, use_container_width=True)



