import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap
import google.generativeai as genai

st.set_page_config(
    page_title="Rivers of India Dashboard",
    #page_icon="🌊",
    layout="wide"
)

try:
    # Configure the Gemini API key from Streamlit secrets
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Google API Key not found in secrets. Please add it to .streamlit/secrets.toml")
        st.stop() 
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

@st.cache_data # Cache the AI responses to avoid repeated calls for the same prompt
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash') 
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

data_url = 'https://github.com/Sathvik-km/Rivers-Dashboard/releases/' \
     'download/data/'

states_gpkg = 'India_states.gpkg'
rivers_gpkg = 'rivers_gdf.gpkg'

@st.cache_data
def load_data(url, filename):
    try:
        gdf = gpd.read_file(url+filename)
        return gdf
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return None



st.title("Rivers Of India Interactive Dashboard")
st.write(
    """This app visualizes the rivers in India. You can select a state to view its rivers.
    Select one or more states below to view their rivers. The width of the line is proportional to the value of 
    upland of each river.
    """
)

with st.sidebar:
    st.header("Dashboard controls")

    with st.spinner("Loading data..."):
        country_gdf = load_data(data_url , states_gpkg)
        rivers_gdf = load_data(data_url , rivers_gpkg)

    states = st.multiselect("Select state(s) to visualize",sorted(country_gdf.name),
                            help="You can select multiple states")
        
    basemap= st.selectbox("Select Basemap",
                            sorted(['CartoDB.DarkMatter', 'CartoDB.Positron', 'OpenStreetMap', 'Esri.WorldImagery','Esri.NatGeoWorldMap','Esri.WorldTopoMap',
                           'Esri.WorldStreetMap','Esri.DeLorme']),
                           index=0)

    if states:
        tab1, tab2 = st.tabs(["Selected Regions Stats", "River Insights"])
        with tab1:
            st.subheader("Selected Regions Stats")
            selected_states = country_gdf[country_gdf.name.isin(states)]
            selected_rivers = gpd.sjoin(rivers_gdf, selected_states, how='inner', predicate= 'intersects')

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Selected States", len(states))

            with col2:
                st.metric("Rivers Found", len(selected_rivers))

        with tab2:
            st.subheader("River Insights (AI Generated)")
            if st.button("Get River Facts for Selected State(s)"):
                if states:
                    states_string = ", ".join(states)
                    prompt = f"""Provide a concise overview of the major rivers in the Indian state(s) of {states_string}.
                        For each major river, briefly mention its significance importance(e.g., cultural, economic, ecological, tributaries, latest news)
                        and one interesting fact. If multiple states are listed, provide a combined overview or key highlights for the region.
                        Keep the response under 300 words.
                        """
                    with st.spinner(f"Waiting for LLM response..."):
                        ai_response = get_gemini_response(prompt)
                        if ai_response:
                            st.markdown(ai_response)
                        else:
                            st.warning("Could not retrieve information from AI at this time.")
                else:
                    st.info("Please select at least one state to get river facts.")

@st.cache_data
def create_basemap(basemap_name="CartoDB.DarkMatter"):
    m = leafmap.Map(
        layer_control = True,
        draw_control=False,
        measure_control=True,
        fullscreen_control=True
    )
    m.add_basemap(basemap_name)
    return m

def style_features(feature):
  width = feature['properties'].get('width',1)
  return {
      'color': '#0066cc',
      'weight': 1+ (width*2),
      'opacity': 0.8
  }

def highlight_function(feature):
    return {
        'color': '#00ccff',
        'weight': feature['properties'].get('width', 1) * 3 + 1 if feature['properties'].get('width') else 3,
        'opacity': 1
    }

# Main part
# Create the map
if states:
    states_gdf = country_gdf[country_gdf.name.isin(states)]
    merged_gdf = gpd.sjoin(rivers_gdf, states_gdf , how='inner', predicate='intersects')

    m = create_basemap(basemap)
    m.add_gdf(states_gdf, layer_name = 'States', style = {'fill_opacity': 0.2, 'fillColor':'#3388ff','color':'#004daa', 'weight':2}, zoom_to_layer=True, info_mode='on_click')
    
    m.add_gdf(merged_gdf, layer_name = 'Rivers', style_callback = style_features, zoom_to_layer=False, info_mode='on_hover', highlight_function= highlight_function)
    map_data = m.to_streamlit(width=800,height=600, use_container_width=True)

else:
    st.info("Please select one or more states to visualize the rivers.")
    m = create_basemap(basemap if 'basemap' in locals() else "CartoDB.DarkMatter")
    m.add(country_gdf,
          layer_name='India States',
          style={
                'fillColor': '#3388ff',
                'color': '#004daa',
                'weight': 1,
                'fillOpacity': 0.1
            },
            zoom_to_layer=True
        )
    map_data = m.to_streamlit(height=600, width=800, use_container_width=True)