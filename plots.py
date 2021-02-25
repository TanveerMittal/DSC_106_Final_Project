import plotly
import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_line_plot(df, complaints):
    # Drop N/A values
    df['CMPLNT_FR_DT'] = df['CMPLNT_FR_DT'].dropna()
    # Extract Year
    df['CMPLNT_FR_YEAR'] = df['CMPLNT_FR_DT'].apply(lambda x: str(x)[6:])
    # Extract Month
    df['CMPLNT_FR_MONTH'] = df['CMPLNT_FR_DT'].apply(lambda x: str(x)[:2])
    # Data starts from 2006, clear junk
    df = df[df['CMPLNT_FR_YEAR'] >= '2006']
    
    # Create figure
    fig = go.Figure()
    years = np.unique(df['CMPLNT_FR_YEAR'])
    
    # If no complaint type specified, plot all complaint types
    if len(complaints) == 0:
        # Month level granularity
        df_line = df.groupby(['CMPLNT_FR_YEAR', 'CMPLNT_FR_MONTH']).count().reset_index()
        df_line['time'] = df_line[['CMPLNT_FR_YEAR', 'CMPLNT_FR_MONTH']].agg('-'.join, axis=1)
        
        # Create traces
        fig.add_trace(go.Scatter(x=df_line['time'], y=df_line['CMPLNT_NUM'],
                        mode='lines+markers',
                        name='Complaints'))
        
        # yearly moving average on same graph
        df_line['MA12'] = df_line['CMPLNT_NUM'].rolling(12).mean()
        fig.add_trace(go.Scatter(x=df_line['time'], y=df_line['MA12'],
                                 mode='lines',
                                 name='1Y Moving Average'))

    # If complaint types specified, loop and plot with moving average
    else:
        for complaint in complaints:
            # Select complaint type
            df_temp = df[df['LAW_CAT_CD'] == complaint]
            # Month level granularity
            df_temp = df_temp.groupby(['CMPLNT_FR_YEAR', 'CMPLNT_FR_MONTH']).count().reset_index()
            df_temp['time'] = df_temp[['CMPLNT_FR_YEAR', 'CMPLNT_FR_MONTH']].agg('-'.join, axis=1)

            # Create traces
            fig.add_trace(go.Scatter(x=df_temp['time'], y=df_temp['CMPLNT_NUM'],
                            mode='lines+markers',
                            name=complaint))

            # yearly moving average on same graph
            df_temp['MA12'] = df_temp['CMPLNT_NUM'].rolling(12).mean()
            fig.add_trace(go.Scatter(x=df_temp['time'], y=df_temp['MA12'],
                                mode='lines',
                                name='{} 1Y Moving Average'.format(complaint)))
            
    # Set x-ticks
    fig.update_layout(
        title="NYPD Complaints over Time",
        xaxis_title="Time(Years)",
        yaxis_title="Number of Complaints",
        title_x=0.5,
        font_size=12,
        xaxis = dict(
            tickmode = 'array',
            tickvals = years,
            ticktext = years,
            tickangle = 45
        )
    )
    
    return fig

def bar_chart(df):
    # Count categories
    cats = df["OFNS_DESC"].value_counts().reset_index(drop=False).rename({"index":"category", "OFNS_DESC": "count"}, axis=1)

    # Filter small category counts
    cats = cats[cats["count"] > 6000]

    # Create and format bar chart
    fig = px.bar(cats, x="count", y="category", orientation='h')
    fig.update_layout(title="NYPD Complaint Frequencies", title_x=0.5, font_size=10,
                      xaxis_title="Number of Complaints", yaxis_title="Criminal Offense Categories", 
                      barmode='stack', yaxis={'categoryorder':'total ascending'})
    return fig

def fill_map(df, year, complaints):
    # Drop N/A values
    df['CMPLNT_FR_DT'] = df['CMPLNT_FR_DT'].dropna()
    # Extract Year
    df['CMPLNT_FR_YEAR'] = df['CMPLNT_FR_DT'].apply(lambda x: str(x)[6:])
    # Extract Month
    df['CMPLNT_FR_MONTH'] = df['CMPLNT_FR_DT'].apply(lambda x: str(x)[:2])
    # Data starts from 2006, clear junk
    df = df[df['CMPLNT_FR_YEAR'] >= '2006']

    # Initialize map
    m = folium.Map(location=[40.7128, -74.0060], tiles='OpenStreetMap')
    
    # Remove junk precincts
    df_map = df[df['ADDR_PCT_CD'] > 0]
    # Filter by year and complaint types
    df_map = df_map[df_map['CMPLNT_FR_YEAR'] == year]
    if len(complaints) > 0:
        df_map = df_map[df_map['LAW_CAT_CD'].isin(complaints)]
    
    # Groupby precinct and calculate number of complaints + centroid of coordinates
    df_map = df_map[['CMPLNT_NUM', 'ADDR_PCT_CD', 'Latitude', 'Longitude']].groupby('ADDR_PCT_CD').agg({
        'CMPLNT_NUM': 'size',
        'Latitude': 'mean',
        'Longitude': 'mean'
    }).reset_index()
    
    # Define radius of point on map
    df_map['Radius'] = df_map['CMPLNT_NUM']/df_map['CMPLNT_NUM'].max() * 10
    
    # Mark point on map, and define popup label
    for each in df_map.iterrows():
        # Show on click
        pop = 'Precinct: {0}, Complaints: {1}'.format(int(each[1].ADDR_PCT_CD), 
                                                      int(each[1].CMPLNT_NUM))
        
        folium.CircleMarker(location=[each[1].Latitude, each[1].Longitude],
                            radius=each[1].Radius, 
                            weight=each[1].Radius,
                            popup=pop).add_to(m)
    
    #Set the zoom to the maximum possible
    m.fit_bounds(m.get_bounds())

    # Save the map to an HTML file
    m.save('simple_dot_plot.html')

    # Display map
    return m

def sankey_diagram(df):
    # Query and clean demographics data
    demographics = df[['OFNS_DESC', 'SUSP_RACE', 'SUSP_SEX', 'VIC_RACE', 'VIC_SEX',]
                    ].replace("UNKNOWN",None).replace("U", None ).replace("D", None
                    ).replace("E", None).replace("OTHER", None).dropna()

    # Define rgb colors for nodes and links
    node_colors = ['rgba(23, 190, 207, 0.8)', 'rgba(44, 160, 44, 0.8)',
                   'rgba(148, 103, 189, 0.8)', 'rgba(188, 189, 34, 0.8)',
                   'rgba(214, 39, 40, 0.8)', 'rgba(227, 119, 194, 0.8)']
    link_colors = [col.replace("0.8", "0.4") for col in node_colors]

    # Construct and populate graph structure
    nodes = list(demographics["SUSP_RACE"].unique()) * 2
    node_mapping = {nodes[i]:i for i in range(len(nodes)//2)}
    race_combo_counts = demographics.groupby(["SUSP_RACE", "VIC_RACE"]).count()
    source = []
    target = []
    value = []
    edge_colors = []
    for i in race_combo_counts.index:
        source.append(node_mapping[i[0]])
        target.append(node_mapping[i[1]] + len(node_mapping))
        value.append(race_combo_counts.loc[i, "OFNS_DESC"])
        edge_colors.append(link_colors[node_mapping[i[0]]])
    
    # Create and format Sankey Diagram
    fig = go.Figure(data=[go.Sankey(
                    node = dict(
                      pad = 15,
                      thickness = 20,
                      line = dict(color = "black", width = 0.5),
                      label = nodes,
                      color = node_colors * 2
                    ),
                    link = dict(
                      source = source,
                      target = target,
                      value = value,
                        color=edge_colors
                  ))])
    fig.update_layout(title_text="Relationships between Suspect Race and Victim Race", font_size=12, title_x=0.5)
    return fig