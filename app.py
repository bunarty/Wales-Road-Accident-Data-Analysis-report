# Import required Python Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import folium
from folium import plugins
from streamlit_folium import folium_static

st.set_page_config(layout = 'wide')

@st.cache

#Load the Wales Accidents Dataset
def load_data():
    accident = pd.read_csv(r'wales_accident.csv')
    accident.reset_index(drop=True, inplace=True)
    return accident

#Load Wales Accidents location Dataset
def load_location_data():
    accident_location = pd.read_csv(r'location.csv')
    accident_location.reset_index(drop=True, inplace=True)
    return accident_location
    
#Main Sidebar navigation    
page = st.sidebar.selectbox('Select page',['Home','Breakdown', 'Heat Map', 'Sankey Diagram'])

#Home page
if page == 'Home':
    accident = load_data()
    st.title('Wales Road Accidents Report')
    st.header('Wales Road Accident records from 2016 to 2020')
    st.markdown('This report aims to provide a documented insight into the analysis of Road Accidents Data of Wales through visuals and text recorded by the Welsh Police force.')
    st.markdown('The former is responsible for the Wales local authorities districts of the United Kingdom.' + 
    ' Road accidents are one of the most critical factors contributing to untimely deaths and economic losses to public and private property.' 
    ' It is important to find sustainable countermeasures to minimise road accidents.'
    ' The efficiency of accident prevention depends on the reliability of reported data, analysis performed and interpretation of results.')
    st.markdown(' Below is a table containing the number of accident cases recorded by the Welsh police forcel from the year 2016 to 2020.' + 
    ' According to the data there were 20881 accident cases within that time period.')
    st.dataframe(accident.head(accident.shape[0]))

#Bar Charts page
elif page == 'Breakdown':
    wales_accident = load_data()
    st.title('Wales Road Accidents Report')
    st.header('Breakdown of Wales Road Accident Data via Bar Charts')
    st.markdown('This page displays the breakdown of accidents that occured in Wales from 2016 to 2020 by comparing the number of accidents in Wales with various other factors producing a series of barcharts in the process.')
    st.markdown('Hovering on each bar in a bar chart gives the exact number of collision cases recorded based on the criteria that the bar represents')
    accident_cols = ['police_force', 'accident_severity','local_authority_district',
                'day_of_week','first_road_class', 'road_type','junction_detail', 'junction_control', 
                'second_road_class', 'pedestrian_crossing_human_control', 'pedestrian_crossing_physical_facilities',
                 'light_conditions', 'weather_conditions', 'road_surface_conditions', 'special_conditions_at_site', 
                 'carriageway_hazards', 'urban_or_rural_area', 'did_police_officer_attend_scene_of_accident']
                 
    #Sidebar navigation for the Bar Charts
    sidebar = st.sidebar
    data_cols = sidebar.selectbox("Select Column:",accident_cols)
  

    data = wales_accident.groupby(data_cols)['accident_index'].count().reset_index().sort_values(by='accident_index')

    #Display bar chart, colour scale and label
    fig = px.bar(data, x='accident_index', y=data_cols,color='accident_index',color_continuous_scale=px.colors.sequential.Inferno, title="Number of accidents per {} (2016-2020)".format(data_cols.replace('_', ' ')))
    fig.update_xaxes(title_text="Number of Accidents")
    fig.update_yaxes(title_text=data_cols.replace('_', ' '))
    st.plotly_chart(fig,use_container_width=True)

#Heat Map page
elif page == 'Heat Map':
    st.title('Wales Road Accidents Report')
    st.header('A Heat Map displaying the Magnitude of Accidents Cases recorded in Wales from 2016 to 2020')
    st.markdown('This page contains a heat map of accidents in Wales from the year 2016 to 2020. The region of South Wales has the highest magnitude of accidents in Wales as depicted by the heat map.')

    wales_accident_location = load_location_data()
    accident_locations = list(zip( wales_accident_location.latitude,  wales_accident_location.longitude))
    def generateHeatMap(default_location=[52.588160, -3.325960], default_zoom_start=7):
        base_map = folium.Map(location=default_location, control_scale=True, tiles="Stamen Toner", zoom_start=default_zoom_start)
        heatmap = plugins.HeatMap(accident_locations, radius=4, blur=2)
        base_map.add_child(heatmap)
        return base_map   
    fig = generateHeatMap()  
    folium_static(fig, width= 1200)

#Sankey Diagram page
else:
    st.title('Wales Road Accidents Report')
    st.header('Visualisation of Wales Road Accident Data via a Sankey (or a Flow) Diagram')
    st.markdown('This page displays a Sankey / flow diagram of accidents in Wales based on some factors such as ' + 
    ' the police force that recorded the accident, whether the accident occurred in an Urban or Rural area, the year that the accident happened and the severity of the accident on the victims.')
    st.markdown('Hovering on a flow line in the Sankey Diagram provides the number of accident cases recorded based on a specific factor.')

    wales_accident = load_data()
    sankey_df = wales_accident.reindex(["police_force","urban_or_rural_area","accident_year","accident_severity"], axis=1)
    col_names = sankey_df.columns.tolist()
    node_labels = []
    num_categorical_vals_per_col = []
    for col in col_names:
        uniques = sankey_df[col].unique().tolist()
        node_labels.extend(uniques)
        num_categorical_vals_per_col.append(len(uniques))   
    source = []
    target = []
    value = []
    colors = []
    for i, num_categories in enumerate(num_categorical_vals_per_col):    
        if i == len(num_categorical_vals_per_col)-1:
            break    
        start_index = sum(num_categorical_vals_per_col[:i])
        start_index_next = sum(num_categorical_vals_per_col[:i+1])
        end_index_next = sum(num_categorical_vals_per_col[:i+2])
    
        col_name = col_names[i]
        next_col_name = col_names[i+1]
    
        grouped_df = sankey_df.groupby([col_name, next_col_name]).size()
    
        for source_i in range(start_index, start_index_next):
            for target_i in range(start_index_next, end_index_next):
                source.append(source_i)
                target.append(target_i)
                source_label = node_labels[source_i]
                target_label = node_labels[target_i]

                try:
                    value.append(grouped_df[source_label][target_label])
                except:
                    value.append(0)
            
                random_color = list(np.random.randint(256, size=3)) + [random.random()]
                random_color_string = ','.join(map(str, random_color))
                colors.append('rgba({})'.format(random_color_string))

    link = dict(source=source, target=target, value=value, color=colors)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = node_labels,
            color = "purple"
            ), 
        link = link)])
    fig.update_layout(title_text="A Sankey Diagram showing the flow of Accidents in Wales based on Police force, Urbarn or Rural area, Accident Year and Accident Serverity factors", font_size=10)
    st.plotly_chart(fig,use_container_width=True)