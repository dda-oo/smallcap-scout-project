import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from yahoo_fin import stock_info as si  # For Yahoo Finance data

# Custom logo and favicon
st.set_page_config(page_title="Stock Predictor", page_icon="favicon.ico")

# Add logo
st.image("logo.png", use_column_width=True)

# Title and description
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Analyze stock performance, compare multiple tickers, predict future growth, and get investment recommendations. 
    Choose a model to analyze predictions using various techniques.
""")

# Step 1: Select a Model from the Dropdown
model_choice = st.selectbox(
    'Choose a model for prediction:',
    ['RNN', 'KNN', 'Logistic Regression']
)

# Step 2: Select the range of quarters (Using a slider)
def quarter_range_slider():
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
    
    return st.select_slider('Select a quarter range:', options=quarter_labels, value=('2010-Q1', '2024-Q4'))

from_quarter, to_quarter = quarter_range_slider()

# Step 3: Allow users to select multiple tickers using a multiselect box
tickers = st.multiselect('Select up to 5 tickers:', ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'MSFT'], default=['AAPL'])

if len(tickers) > 5:
    st.error("You can select a maximum of 5 tickers.")
else:
    st.write(f"Selected tickers: {', '.join(tickers)}")

# Step 4: Fetch company summaries (e.g., market cap, sector, etc.)
def fetch_company_summary(ticker):
    try:
        summary = si.get_quote_table(ticker)
        st.write(f"### {ticker} Summary")
        st.json(summary)
    except Exception as e:
        st.error(f"Could not fetch summary for {ticker}")

if tickers:
    for ticker in tickers:
        fetch_company_summary(ticker)

# Step 5: Fetch performance and predictions from external service
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

        # Extract predictions and recommendations from the JSON response
        predictions = data.get('predictions', [])
        recommendations = data.get('recommendations', [])

        # Step 6: Display historical performance
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            ticker_performance = pd.DataFrame(ticker_data['data'])

            st.write(f"Performance for {ticker}:")
            st.line_chart(ticker_performance)

        # Step 7: Display predictions for quarter ahead, year ahead, 2 years ahead
        st.write("### Predictions")
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            st.write(f"Predictions for {ticker}:")
            for year in ['quarter_ahead', 'year_ahead', '2_year_ahead']:
                st.write(f"{year}: {ticker_data['data'].get(year)}")

        # Step 8: Display investment recommendations
        st.write("### Investment Recommendations")
        for recommendation in recommendations:
            ticker = recommendation['ticker']
            advice = recommendation['advice']
            st.write(f"**{ticker}:** {advice}")
    else:
        st.error("Failed to fetch data from external service.")

# Step 9: Yahoo Finance News Fetching
st.write("### Latest News on Selected Tickers")
for ticker in tickers:
    st.write(f"#### News for {ticker}")
    try:
        news = si.get_news(ticker)
        for item in news[:5]:  # Display only top 5 news items
            st.write(f"- {item['title']}: {item['link']}")
    except Exception as e:
        st.error(f"Could not fetch news for {ticker}")
