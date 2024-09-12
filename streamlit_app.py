import streamlit as st
import pandas as pd
import requests
import json

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Predictor",
    page_icon="images/favicon.ico",  # Ensure favicon is in the "images" folder
    layout="wide"  # Optional: Makes the layout wider for better visibility
)

# Sidebar layout for form inputs
st.sidebar.header("Configure your analysis")

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo1.png", width=170)  # Ensure logo is in the "images" folder

# Title and description (centered on the main page)
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Analyze stock performance and predict future stock growth.
    Choose a model to analyze predictions for individual tickers using RNN or XGB models.
""")

# Load the available tickers dynamically from a CSV file
@st.cache
def load_tickers():
    tickers_df = pd.read_csv('data/cik_ticker_pairs.csv')  # Ensure this path is correct
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Step 1: Select a model from the dropdown (limited to RNN and XGB)
model_choice = st.sidebar.selectbox(
    'Choose a model for prediction:',
    ['RNN', 'XGB']
)

# Step 2: Select a quarter (not a range, and limited to 2024-Q3)
def quarter_selection():
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3']]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters if not (year == 2024 and quarter == 'Q4')]
    return st.sidebar.selectbox('Select a quarter:', options=quarter_labels, index=len(quarter_labels) - 1)

selected_quarter = quarter_selection()

# Step 3: Select a single ticker (limited to one ticker at a time)
selected_ticker = st.sidebar.selectbox('Select a ticker:', available_tickers)

# Step 4: Additional parameters for the request
sequence = st.sidebar.slider('Select Sequence Length:', min_value=1, max_value=12, value=4)
horizon = st.sidebar.selectbox('Select Prediction Horizon:', ['quarter-ahead', 'year-ahead'])
threshold = st.sidebar.slider('Select Threshold (%):', min_value=10, max_value=100, step=10, value=50)
small_cap = st.sidebar.checkbox('Small Cap Only?', value=True)

# Ensure only one ticker is processed
st.sidebar.write(f"Selected ticker: {selected_ticker}")

# Fetch performance and predictions from the external service
if selected_ticker:
    st.write(f"Displaying {model_choice} model predictions for ticker: {selected_ticker}")
    
    # API URL
    api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
    
    # Parameters for the FastAPI request
    params = {
        'ticker': selected_ticker,
        'model_type': model_choice.lower(),  # API expects lowercase model type
        'quarter': selected_quarter,  # The selected quarter
        'sequence': sequence,  # Sequence length
        'horizon': horizon,  # Prediction horizon
        'threshold': f"{threshold}%",  # Threshold as a percentage
        'small_cap': str(small_cap).lower()  # Convert boolean to lowercase string ('true'/'false')
    }
    
    # Send the request to the FastAPI endpoint
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Display the API response
        st.write(f"**Ticker:** {data['ticker']}")
        st.write(f"**Model Type:** {data['model_type']}")
        st.write(f"**Prediction:** {data['prediction']}")
        st.write(f"**Worthiness:** {data['worthiness']}")
        st.write(f"**Quarter:** {data['quarter']}")
        st.write(f"**Sequence:** {data['sequence']}")
        st.write(f"**Horizon:** {data['horizon']}")
        st.write(f"**Threshold:** {data['threshold']}")
        st.write(f"**Small Cap:** {data['small_cap']}")
    else:
        st.error(f"Failed to fetch data for {selected_ticker}. Response code: {response.status_code}")

# Display disclaimer at the bottom of the sidebar or main page
st.sidebar.markdown("<br><br><hr>", unsafe_allow_html=True)  # Adds a separator line
st.sidebar.markdown(
    """
    <div style='font-size: 0.9em; font-style: italic; color: #666;'>
    This project is for educational purposes only. The predictions and information provided here are not financial advice.
    Please consult a professional financial advisor for investment decisions.
    </div>
    """,
    unsafe_allow_html=True
)
