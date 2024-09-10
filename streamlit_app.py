import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests  # For sending requests to the external service
from datetime import datetime

# Title and description
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Enter one or more stock tickers to analyze their performance, 
    predict their future market cap, and get an investment recommendation.
""")

# Step 1: Select the range of years (Using a radio button or slider)
from_year, to_year = st.slider('Select the range of years:', 2010, 2024, (2010, 2024))

# Step 2: Allow users to select multiple tickers using a multiselect box
tickers = st.multiselect('Select up to 5 tickers:', ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'MSFT'], default=['AAPL', 'TSLA'])

# Limit the number of tickers to 5
if len(tickers) > 5:
    st.error("You can select a maximum of 5 tickers.")
else:
    # Display the selected tickers
    st.write(f"Selected tickers: {', '.join(tickers)}")

# Step 3: Fetch performance and predictions from external service
if tickers:
    st.write(f"Displaying performance from {from_year} to {to_year} for tickers: {', '.join(tickers)}")
    
    # Sending request to external service
    api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
    params = {
        'tickers': ','.join(tickers),
        'from_year': from_year,
        'to_year': to_year
    }

    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract predictions and recommendations from the JSON response
        predictions = data.get('predictions', [])
        recommendations = data.get('recommendations', [])
        
        # Step 4: Display historical performance (Assuming the external service returns it)
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            ticker_performance = pd.DataFrame(ticker_data['data'])
            
            st.write(f"Performance for {ticker}:")
            st.line_chart(ticker_performance)
        
        # Step 5: Display predictions for 1, 2, and 3 years ahead
        st.write("### Predictions for 1, 2, and 3 Years Ahead")
        for ticker_data in predictions:
            ticker = ticker_data['ticker']
            st.write(f"Predictions for {ticker}:")
            for year in ticker_data['data'].keys():
                st.write(f"{year}: {ticker_data['data'][year]}")
        
        # Step 6: Display investment recommendations
        st.write("### Investment Recommendations")
        for recommendation in recommendations:
            ticker = recommendation['ticker']
            advice = recommendation['advice']
            st.write(f"**{ticker}:** {advice}")
    else:
        st.error("Failed to fetch data from external service.")
