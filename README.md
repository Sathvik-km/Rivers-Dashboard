# River Data Analysis Project

This project analyzes river data using GeoPandas and visualizes it with Streamlit.

## Setup

1. Clone this repository
2. Create conda streamlit environment: 
3. Activate environment: `conda activate river_env`
4. Run Streamlit app: `streamlit run rivers/main.py`

## Data

The project uses GPKG files stored in this directory.

## API Keys and Secrets

This application requires the following API keys:

1. **Gemini API Key**: Required for AI-powered river insights

### Local Development Setup

1. Create a `.streamlit/secrets.toml` file in the project root
2. Add your API keys using the format in `.streamlit/secrets.example.toml`