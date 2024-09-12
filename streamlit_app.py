import streamlit as st
import pandas as pd
import requests
import json
import http.client
import urllib

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Predictor",
    page_icon="images/favicon.ico",  # Ensure favicon is in the "images" folder
    layout="wide"  # Optional: Makes the layout wider for better visibility
)

# Sidebar layout for form inputs
st.sidebar.header("Configure your analysis")

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo2.png", width=170)  # Ensure logo is in the "images" folder

# Title and description (centered on the main page)
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Analyze stock performance and predict future stock growth.
    Choose a model to analyze predictions for individual tickers using RNN or XGB models.
""")

# Load the available tickers dynamically from a CSV file
@st.cache_data
def load_tickers():
    tickers_df = pd.read_csv('data/cik_ticker_pairs.csv')  # Ensure this path is correct
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Step 1: Select a model from the dropdown (limited to rnn and xgb)
model_choice = st.sidebar.selectbox(
    'Choose a model for prediction:',
    ['rnn', 'xgb']  # Models in lowercase
)

# Step 2: Select a quarter (limited to 2024-Q2)
def quarter_range_slider():
    # Limit to June 2024 (Q2 of 2024) and go back to 2010
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4'] if not (y == 2024 and q == 'Q3') and not (y == 2024 and q == 'Q4')]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]

    # Reverse the order to show from 2024-Q2 down to 2010-Q1
    quarter_labels.reverse()

    return st.sidebar.selectbox('Select a quarter:', options=quarter_labels, index=0)

# Call the function to get the selected quarter
selected_quarter = quarter_range_slider()

# Step 3: Select a single ticker (limited to one ticker at a time)
selected_ticker = st.sidebar.selectbox('Select a ticker:', available_tickers)

# Step 4: Additional parameters for the request (sequence removed)
horizon = st.sidebar.selectbox('Select Prediction Horizon:', ['quarter-ahead', 'year-ahead', 'two-years-ahead'])
threshold = st.sidebar.selectbox('Growth Threshold (%):', [30, 50])  # Offering only 30% and 50% as options
small_cap = st.sidebar.checkbox('Small Cap Only?', value=True)

# Ensure only one ticker is processed
st.sidebar.write(f"Selected ticker: {selected_ticker}")

# Section to display Ticker and Model Type
if selected_ticker:
    st.write(f"Displaying {model_choice.upper()} model predictions for ticker: {selected_ticker}")
    st.write(f"**Ticker:** {selected_ticker}")
    st.write(f"**Model Type:** {model_choice.upper()}")

    # API URL for predictions
    prediction_api_url = 'https://smallcapscoutupdate-196636255726.europe-west1.run.app/predict'

    # Parameters for the FastAPI prediction request
    prediction_params = {
        'ticker': selected_ticker,
        'model_type': model_choice,  # API expects lowercase model type
        'quarter': selected_quarter,  # The selected quarter
        'horizon': horizon,  # Prediction horizon
        'threshold': f"{threshold}%",  # Threshold as a percentage (30% or 50%)
        'small_cap': str(small_cap).lower()  # Convert boolean to lowercase string ('true'/'false')
    }

    # Send the prediction request to the FastAPI endpoint
    response = requests.get(prediction_api_url, params=prediction_params)

    if response.status_code == 200:
        data = response.json()

        # Section to display company info
        st.subheader("Additional Information")
        info_api_url = f'https://smallcapscoutupdate-196636255726.europe-west1.run.app/info?ticker={selected_ticker}'
        info_response = requests.get(info_api_url)

        if info_response.status_code == 200:
            info_data = info_response.json()
            st.write(f"**Company name:** {info_data['Company name']}")
            st.write(f"**Market cap:** {info_data['Market cap']}")
            st.write(f"**Revenues:** {info_data['Revenues']}")
            st.write(f"**Gross Profit:** {info_data['Gross Profit']}")
            st.write(f"**Net Income:** {info_data['Net Income']}")
            st.write(f"**Operating Cash Flows:** {info_data['Operating Cash Flows']}")
        else:
            st.error("Failed to fetch company information.")

        # Section to display predictions
        st.subheader("Prediction Results")
        worthiness = data.get('worthiness', 'Unknown')

        if worthiness == 'worthy':
            st.write(f"**Worthiness:** {worthiness}. Based on our deep analytics, this stock seems promising!")
        else:
            st.write(f"**Worthiness:** {worthiness}. Unfortunately, our data suggests this stock might not be the best investment.")

    else:
        st.error(f"Failed to fetch predictions for {selected_ticker}. Response code: {response.status_code}")

# Function to fetch stock news using Marketaux API
def fetch_stock_news_marketaux(tickers):
    if not tickers:  # Check if there are selected tickers
        return []

    conn = http.client.HTTPSConnection('api.marketaux.com')
    params = urllib.parse.urlencode({
        'api_token': 'ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm',  # The actual API token
        'symbols': ','.join(tickers),
        'limit': 5  # Adjust the limit as needed
    })

    conn.request('GET', '/v1/news/all?{}'.format(params))
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        news_data = json.loads(data.decode('utf-8'))
        return news_data.get('data', [])
    else:
        st.error("Failed to fetch news.")
        return []

# Display news for the selected ticker in the sidebar
if selected_ticker:
    st.sidebar.header("Latest News")
    news_data = fetch_stock_news_marketaux([selected_ticker])  # Fetch news for the selected ticker

    # Display news items in the sidebar
    for item in news_data:
        title = item.get('title', 'No Title Available')  # Fallback if title is not found
        link = item.get('url', '#')  # Use 'url' or a fallback if the key is not found
        st.sidebar.write(f"- **{title}**: [Read more]({link})")

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
