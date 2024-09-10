import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import http.client, urllib.parse

# Function to fetch stock news from Marketaux API
def fetch_stock_news(tickers):
    conn = http.client.HTTPSConnection('api.marketaux.com')
    
    # Dynamically setting tickers selected by the user
    params = urllib.parse.urlencode({
        'api_token': 'ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm',
        'symbols': ','.join(tickers),  # Join selected tickers with commas
        'limit': 5  # You can adjust this limit as needed
    })
    
    conn.request('GET', '/v1/news/all?{}'.format(params))
    res = conn.getresponse()
    data = res.read()
    
    # Parse JSON response
    news_data = json.loads(data.decode('utf-8'))
    return news_data

# Function to load historical stock data (dummy data for now)
@st.cache
def load_data(tickers):
    dates = pd.date_range(start="2010-01-01", end="2024-01-01", freq="Q")
    data = {ticker: np.random.normal(loc=100, scale=20, size=len(dates)) for ticker in tickers}
    return pd.DataFrame(data, index=dates)

# Function to predict future performance (dummy logic)
def predict_future(data, quarters_ahead):
    future_data = data.iloc[-1] * (1 + np.random.normal(loc=0.05, scale=0.10, size=(quarters_ahead, len(data.columns))))
    future_dates = pd.date_range(start=data.index[-1], periods=quarters_ahead+1, freq='Q')[1:]
    return pd.DataFrame(future_data, index=future_dates, columns=data.columns)

# Function to recommend investment (dummy logic)
def recommend_investment(ticker_data):
    recommendation = "Good Investment" if ticker_data.iloc[-1] > ticker_data.mean() else "Risky Investment"
    return recommendation

# Main Streamlit app code
st.title("Stock Performance and News Dashboard")

# Step 1: Select tickers with a multiselect box
tickers = st.multiselect('Select up to 5 tickers:', ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'MSFT'], default=['AAPL'])

# Limit to 5 tickers
if len(tickers) > 5:
    st.error("You can select a maximum of 5 tickers.")
else:
    st.write(f"Selected tickers: {', '.join(tickers)}")

    # Step 2: Select quarters (2010-2024)
    quarter_range = st.slider('Select the range of quarters:', 2010.0, 2024.0, (2010.0, 2024.0), step=0.25)
    from_year = int(quarter_range[0])
    to_year = int(quarter_range[1])

    # Step 3: Choose a prediction model
    model_choice = st.selectbox('Choose a prediction model:', ['RNN', 'KNN', 'Logistic Regression'])
    st.write(f"Selected model: {model_choice}")

    # Load historical performance data (dummy)
    data = load_data(tickers)
    filtered_data = data[(data.index.year >= from_year) & (data.index.year <= to_year)]

    # Step 4: Display historical performance
    if tickers:
        st.write(f"Displaying performance from {from_year} to {to_year} for tickers: {', '.join(tickers)}")
        st.line_chart(filtered_data)

        # Step 5: Predict future performance for quarter ahead, year ahead, and 2 years ahead
        st.write("### Predictions for Quarter Ahead, Year Ahead, and 2 Years Ahead")
        
        predictions_1quarter = predict_future(filtered_data, 1)
        predictions_1year = predict_future(filtered_data, 4)
        predictions_2years = predict_future(filtered_data, 8)
        
        st.write("#### Quarter Ahead Prediction")
        st.line_chart(predictions_1quarter)
        
        st.write("#### Year Ahead Prediction")
        st.line_chart(predictions_1year)
        
        st.write("#### 2 Years Ahead Prediction")
        st.line_chart(predictions_2years)

        # Step 6: Investment Recommendations
        st.write("### Investment Recommendations")
        for ticker in tickers:
            recommendation = recommend_investment(filtered_data[ticker])
            st.write(f"**{ticker}:** {recommendation}")

        # Step 7: Fetch and display stock news
        st.write("### Latest News on Selected Tickers")
        try:
            news_data = fetch_stock_news(tickers)
            for article in news_data.get('data', []):
                st.write(f"**{article['title']}**")
                st.write(f"{article['description']}")
                st.write(f"[Read more]({article['url']})")
                st.write("---")
        except Exception as e:
            st.error(f"Failed to fetch news: {e}")

# Add logo and favicon
st.sidebar.image("path_to_your_logo.png", use_column_width=True)  # Replace with actual logo path
st.set_page_config(page_title="Stock Performance Dashboard", page_icon="path_to_your_favicon.ico")  # Replace with actual favicon path
