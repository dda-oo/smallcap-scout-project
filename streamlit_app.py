import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import http.client
import urllib.parse
from yahoo_fin import stock_info as si  # For Yahoo Finance data

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Predictor", 
    page_icon="images/favicon.ico",  # Ensure favicon is in the "images" folder
    layout="wide"  # Optional: Makes the layout wider for better visibility
)

# Sidebar layout for form inputs
st.sidebar.header("Configure your analysis")

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo1.png", width=120)  # Ensure logo is in the "images" folder

# Title and description (centered on the main page)
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Analyze stock performance, compare multiple tickers, predict future growth, and get investment recommendations. 
    Choose a model to analyze predictions using various techniques.
""")

# Load the available tickers dynamically from a CSV file
@st.cache
def load_tickers():
    tickers_df = pd.read_csv('data/sample.csv')  # Ensure this path is correct
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Step 1: Select a model from the dropdown
model_choice = st.sidebar.selectbox(
    'Choose a model for prediction:',
    ['RNN', 'KNN', 'Logistic Regression']
)

# Step 2: Select the range of quarters (slider in the sidebar)
def quarter_range_slider():
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
    return st.sidebar.select_slider('Select a quarter range:', options=quarter_labels, value=('2010-Q1', '2024-Q4'))

from_quarter, to_quarter = quarter_range_slider()

# Step 3: Allow users to dynamically select tickers using a multiselect box in the sidebar
tickers = st.sidebar.multiselect('Select up to 5 tickers:', available_tickers)

# Limit tickers
if len(tickers) > 5:
    st.sidebar.error("You can select a maximum of 5 tickers.")
else:
    st.sidebar.write(f"Selected tickers: {', '.join(tickers)}")

# Fetch news for the selected tickers from the Marketaux API
def fetch_stock_news_marketaux(tickers):
    if not tickers:  # Check if there are selected tickers
        return []
    
    conn = http.client.HTTPSConnection('api.marketaux.com')
    params = urllib.parse.urlencode({
        'api_token': 'ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm',  # The actual API token
        'symbols': ','.join(tickers),
        'limit': 5  # Could be adjusted this limit as needed
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

# Display news for the selected tickers in the sidebar
if tickers:
    st.sidebar.header("Latest News")
    news_data = fetch_stock_news_marketaux(tickers)  # Fetch news for selected tickers

    # Display news items in the sidebar
    for item in news_data:
        title = item.get('title', 'No Title Available')  # Fallback if title is not found
        link = item.get('url', '#')  # Use 'url' or a fallback if the key is not found
        st.sidebar.write(f"- **{title}**: [Read more]({link})")

# Fetch performance and predictions from the external service
if tickers:
    st.write(f"Displaying performance from {from_quarter} to {to_quarter} for tickers: {', '.join(tickers)}")
    api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
    params = {
        'tickers': ','.join(tickers),
        'from_quarter': from_quarter,
        'to_quarter': to_quarter,
        'model': model_choice
    }
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        predictions = data.get('predictions', [])
        recommendations = data.get('recommendations', [])

        # Display historical performance
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            ticker_performance = pd.DataFrame(ticker_data['data'])
            st.write(f"Performance for {ticker}:")
            st.line_chart(ticker_performance)

        # Display predictions for quarter ahead, year ahead, 2 years ahead
        st.write("### Predictions")
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            st.write(f"Predictions for {ticker}:")
            for year in ['quarter_ahead', 'year_ahead', '2_year_ahead']:
                st.write(f"{year}: {ticker_data['data'].get(year)}")

        # Display investment recommendations
        st.write("### Investment Recommendations")
        for recommendation in recommendations:
            ticker = recommendation['ticker']
            advice = recommendation['advice']
            st.write(f"**{ticker}:** {advice}")
    else:
        st.error("Failed to fetch data from external service.")

def show_disclaimer_sidebar():
    st.sidebar.markdown(
        """
        **Disclaimer:**  
        This application is for informational purposes only and does not constitute financial advice.  
        Please consult a professional before making investment decisions.
        """, 
        unsafe_allow_html=True
    )

# Show disclaimer in the sidebar
show_disclaimer_sidebar()
