import streamlit as st
import streamlit.components.v1 as stc
from streamlit_folium import folium_static
import pandas as pd
from plots import *

def main():
   df = pd.read_csv("data/NYPD_Complaint_Data_Historic.csv")
   st.title("DSC 106 Final Project")
   st.subheader("Created by Team Beeg Data")
   st.subheader("Team Members: Tanveer Mittal, and Arjun Sawhney")
   st.subheader("")
   st.markdown("# Plot #1:")
   st.plotly_chart(create_line_plot(df))
   st.markdown("# Plot #2:")
   st.plotly_chart(bar_chart(df))
   st.markdown("# Plot #3:")
   folium_static(fill_map(df, '2019', ['FELONY']))
   st.markdown("# Plot #4:")
   st.plotly_chart(sankey_diagram(df))


if __name__ == '__main__':
   #init_models()
   main()