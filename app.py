import streamlit as st
import streamlit.components.v1 as stc
from streamlit_folium import folium_static
import pandas as pd
from plots import *

def main():
    # About Text
    st.title("DSC 106 Final Project")
    st.subheader("Created by Team Beeg Data")
    st.subheader("Team Members: Tanveer Mittal and Arjun Sawhney")
    st.subheader("")

    # Button to render plots
    render = st.button("Render Plots")

    # Load in and cache data
    df = load_data("data/NYPD_Complaint_Data_Historic.csv")

    # Render Line Plot
    st.markdown("# Line Plot of NYPD Complaints Since 2006:")
    complaints = st.multiselect("Select Complaint Types to plot or select none to aggregate all 3:", ["Felony", "Misdemeanor", "Violation"],key=1)
    if render:
        complaints = [c.upper() for c in complaints]
        st.plotly_chart(get_plot_1(df, complaints)["plot"])

    # Render Bar Chart
    st.markdown("# Bar Chart of Criminal Offenses:")
    if render:
        st.plotly_chart(get_plot_2(df)["plot"])

    # Render Heatmap
    st.markdown("# Proprtional Symbol Map of NYPD Complaints by Precinct:")
    year = st.slider("Select year to plot:", min_value=2006, max_value=2019)
    complaints_2 = st.multiselect("Select Complaint Types to plot or select none to aggregate all 3:", ["Felony", "Misdemeanor", "Violation"], key=2)
    if render:
        complaints_2 = [c.upper() for c in complaints_2]
        folium_static(get_plot_3(df, year, complaints_2)["plot"])
    
    # Render Sankey Diagram
    st.markdown("# Sankey Diagram of Suspect and Victim Races:")
    if render:
        st.plotly_chart(get_plot_4(df)["plot"])


@st.cache(allow_output_mutation=True)
def load_data(path):
    return pd.read_csv(path)

@st.cache(hash_funcs={dict: lambda _: None})
def get_plot_1(df, complaints):
    return {"plot":create_line_plot(df, complaints)}

@st.cache(hash_funcs={dict: lambda _: None})
def get_plot_2(df):
    return {"plot": bar_chart(df)}

@st.cache(hash_funcs={dict: lambda _: None})
def get_plot_3(df, year, complaints):
    return {"plot": fill_map(df, str(year), complaints)}

@st.cache(hash_funcs={dict: lambda _: None})
def get_plot_4(df):
    return {"plot": sankey_diagram(df)}


if __name__ == '__main__':
   main()

