import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Load any required data 
@st.cache
def load_data(tickers):
    # Replace with actual data loading logic 
    # Simulated data for example purposes
    dates = pd.date_range(start="2010-01-01", end="2024-01-01", freq="M")
    data = {ticker: np.random.normal(loc=100, scale=20, size=len(dates)) for ticker in tickers}
    return pd.DataFrame(data, index=dates)

# Title and description
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Enter one or more stock tickers to analyze their performance, 
    predict their future market cap, and get an investment recommendation.
""")

# Step 1: Select the range of years
years_range = st.slider('Which years are you interested in?', 2010, 2024, (2010, 2024))

# Step 2: Select the tickers
tickers = st.text_input('Enter up to 4 tickers separated by commas (e.g., AAPL, TSLA, AMZN):', 'AAPL, TSLA')

# Limit the number of tickers
tickers = [ticker.strip().upper() for ticker in tickers.split(',')][:4]

# Step 3: Display historical performance graph
if tickers:
    st.write(f"Displaying performance from {years_range[0]} to {years_range[1]} for tickers: {', '.join(tickers)}")
    
    # Load and filter data for the selected years
    data = load_data(tickers)
    filtered_data = data[(data.index.year >= years_range[0]) & (data.index.year <= years_range[1])]

    st.line_chart(filtered_data)
    
    # Plot with Matplotlib (optional for more customization)
    fig, ax = plt.subplots()
    filtered_data.plot(ax=ax)
    st.pyplot(fig)

# Step 4: Predict future values (using dummy logic here for illustration)
def predict_future(data, years_ahead):
    # Replace this logic with your prediction model (Logistic Regression, etc.)
    future_data = data.iloc[-1] * (1 + np.random.normal(loc=0.05, scale=0.10, size=(years_ahead, len(data.columns))))
    future_dates = pd.date_range(start=data.index[-1], periods=years_ahead+1, freq='Y')[1:]
    return pd.DataFrame(future_data, index=future_dates, columns=data.columns)

if tickers:
    st.write("### Predictions for 1, 2, and 3 Years Ahead")

    # Predict for 1-year, 2-year, and 3-year ahead
    predictions_1year = predict_future(filtered_data, 1)
    predictions_2year = predict_future(filtered_data, 2)
    predictions_3year = predict_future(filtered_data, 3)

    # Plot predictions
    st.write("#### 1-Year Prediction")
    st.line_chart(predictions_1year)

    st.write("#### 2-Year Prediction")
    st.line_chart(predictions_2year)

    st.write("#### 3-Year Prediction")
    st.line_chart(predictions_3year)

# Step 5: Investment Recommendation
def recommend_investment(ticker_data):
    # This is dummy logic. Replace it with your actual recommendation logic
    # For example, based on a threshold, previous growth rate, etc.
    recommendation = "Good Investment" if ticker_data.iloc[-1] > ticker_data.mean() else "Risky Investment"
    return recommendation

if tickers:
    st.write("### Investment Recommendations")
    for ticker in tickers:
        recommendation = recommend_investment(filtered_data[ticker])
        st.write(f"**{ticker}:** {recommendation}")
