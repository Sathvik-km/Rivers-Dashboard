import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap

country_gdf = gpd.read_file("D:\Sathvik\streamlit\Rivers\India_states.gpkg")
rivers_gdf = gpd.read_file(r"D:\Sathvik\streamlit\Rivers\rivers_gdf.gpkg")

st.title("Rivers in India")
st.write(
    "This app visualizes the rivers in India. You can select a state to view its rivers."
)

states = st.multiselect("Select a state",sorted(country_gdf.name))
st.write(states)
country_gdf