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



@st.cache
# Load the Wales Accidents Dataset
def load_data():
    accident = pd.read_csv(r'wales_accident.csv')
    accident.reset_index(drop=True, inplace=True)
    return accident

#Load Wales Accidents location Dataset
def load_location_data():
    accident_location = pd.read_csv(r'location.csv')
    accident_location.reset_index(drop=True, inplace=True)
    return accident_location

page = st.sidebar.selectbox('Select page',['Homepage','Breakdown', 'HeatMap', 'Sankey'])

if page == 'Homepage':
    accident = load_data()
    st.title('Wales Road Accidents Report from 2016 to 2020')
    st.header('Wales Road Accident Data Analysis and Visualisation')
    st.markdown('This page displays a dataset containing details on the Accidents in Wales')

    st.dataframe(accident.head(accident.shape[0]))

elif page == 'Breakdown':
    wales_accident = load_data()
    st.title('Wales Road Accidents Report from 2016 to 2020')
    st.header('Wales Road Accident Data Analysis and Visualisation')
    st.markdown('This page displays a bar chart that gives more insight to the accidents that occured in Wales from the year 2016 to 2020.')

    #
    accident_cols = ['police_force', 'accident_severity',
                'day_of_week','first_road_class', 'road_type','junction_detail', 'junction_control', 'local_authority_district',
                'second_road_class', 'pedestrian_crossing_human_control', 'pedestrian_crossing_physical_facilities',
                 'light_conditions', 'weather_conditions', 'road_surface_conditions', 'special_conditions_at_site', 
                 'carriageway_hazards', 'urban_or_rural_area', 'did_police_officer_attend_scene_of_accident']

    #Side bar navigation for the Bar Charts
    sidebar = st.sidebar
    data_cols = sidebar.selectbox("Select Column:",accident_cols)

    data = wales_accident.groupby(data_cols)['accident_index'].count().reset_index().sort_values(by='accident_index')

    #Display bar chart and colour scale
    fig = px.bar(data, x='accident_index', y=data_cols, color='accident_index', 
    color_continuous_scale=px.colors.sequential.Inferno, 

    title="Number of accidents per {} (2016-2020)".format(data_cols.replace('_', ' ')))

    st.plotly_chart(fig,use_container_width=True)

elif page == 'HeatMap':
    st.title('Wales Road Accidents Report from 2016 to 2020')
    st.header('Wales Road Accident Data Analysis and Visualisation')
    st.markdown('This page displays a Heat map of accidents in Wales')

    wales_accident_location = load_location_data()
    accident_locations = list(zip( wales_accident_location.latitude,  wales_accident_location.longitude))
    def generateHeatMap(default_location=[52.588160, -3.325960], default_zoom_start=7):
        base_map = folium.Map(location=default_location, control_scale=True, tiles="Stamen Toner", zoom_start=default_zoom_start)
        heatmap = plugins.HeatMap(accident_locations, radius=4, blur=2)
        base_map.add_child(heatmap)
        return base_map   
    fig = generateHeatMap()  
    folium_static(fig)

else:
    st.title('Wales Road Accidents Report from 2016 to 2020')
    st.header('Wales Road Accident Data Analysis and Visualisation')
    st.markdown('This page displays a sankey or flow diagram of accidents in Wales'
     + 'through the Police force, Urbarn or Rural area, accident year and accident severity')

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
    fig.update_layout(title_text="Sankey Diagram of Accidents in Wales", font_size=10)
    st.plotly_chart(fig,use_container_width=True)
