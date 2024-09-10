import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from yahoo_fin import stock_info as si  # For Yahoo Finance data

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Predictor", 
    page_icon="images/favicon.ico",  # Ensure favicon is in the "images" folder
    layout="wide"  # Optional: Makes the layout wider for better visibility
)

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo.png", width=120)  # Ensure logo is in the "images" folder

# Title and description (centered on the main page)
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Analyze stock performance, compare multiple tickers, predict future growth, and get investment recommendations. 
    Choose a model to analyze predictions using various techniques.
""")

# Load the available tickers dynamically from a CSV file
@st.cache
def load_tickers():
    # Assuming the CSV file has a column called 'Ticker'
    tickers_df = pd.read_csv('data/abbot_sample.csv')  # Replace with the actual file path
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Sidebar layout for form inputs
st.sidebar.header("Configure your analysis")

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

# Fetch company summaries for each selected ticker
def fetch_company_summary(ticker):
    try:
        summary = si.get_quote_table(ticker)
        st.write(f"### {ticker} Summary")
        st.json(summary)
    except Exception as e:
        st.error(f"Could not fetch summary for {ticker}")

# Display company summaries for selected tickers
if tickers:
    for ticker in tickers:
        fetch_company_summary(ticker)

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

# Fetch latest news for the selected tickers from Yahoo Finance
def fetch_stock_news_marketaux(tickers):
    conn = http.client.HTTPSConnection('api.marketaux.com')
    
    params = urllib.parse.urlencode({
        'api_token': 'ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm',
        'symbols': ','.join(tickers),
        'limit': 5  # You can adjust this limit as needed
    })
    
    conn.request('GET', '/v1/news/all?{}'.format(params))
    res = conn.getresponse()
    data = res.read()
    
    news_data = json.loads(data.decode('utf-8'))
    return news_data

# Display news for each ticker
for ticker in tickers:
    st.write(f"#### News for {ticker}")
    fetch_news_yahoo_finance(ticker)  # You can switch to `fetch_stock_news_marketaux(tickers)` if needed

GET https://api.marketaux.com/v1/news/all?symbols=AAPL,TSLA&filter_entities=true&api_token=ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm

