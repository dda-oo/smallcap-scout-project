import streamlit as st
import pandas as pd
import requests
import json
import http.client
import urllib.parse

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Analysis and Prediction Dashboard",
    page_icon="images/favicon.ico",  # Ensure favicon is in the "images" folder
    layout="wide"  # Optional: Makes the layout wider for better visibility
)

# Sidebar layout for form inputs
st.sidebar.header("Configure Your Analysis")

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo2.png", width=170)  # Ensure logo is in the "images" folder

# Title and description (centered on the main page)
st.title("Stock Analysis and Prediction Dashboard")
st.write("""
    This application provides insights into stock performance and predicts future growth for individual tickers.
    Choose a model to analyze predictions and explore additional information related to selected stocks.
""")

# Load the available tickers dynamically from a CSV file
@st.cache
def load_tickers():
    tickers_df = pd.read_csv('data/cik_ticker_pairs.csv')  # Ensure this path is correct
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Step 1: Select a model from the dropdown (limited to rnn and xgb)
model_choice = st.sidebar.selectbox(
    'Choose a model for prediction:',
    ['rnn', 'xgb']
)

# Step 2: Select a quarter (including all quarters and defaulting to 2024-Q2)
def quarter_range_slider():
    # Include all quarters from 2010 to 2024 and set the default index to 2024-Q2
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]

    # Reverse the order to show from 2024-Q2 down to 2010-Q1
    quarter_labels.reverse()

    return st.sidebar.selectbox('Select a quarter:', options=quarter_labels, index=quarter_labels.index('2024-Q2'))

# Call the function to get the selected quarter
selected_quarter = quarter_range_slider()

# Step 3: Select a single ticker (limited to one ticker at a time)
selected_ticker = st.sidebar.selectbox('Select a ticker:', available_tickers)

# Step 4: Additional parameters for the request
horizon = st.sidebar.selectbox('Select Prediction Horizon:', ['quarter-ahead', 'year-ahead', 'two-years-ahead'])
growth_threshold = st.sidebar.selectbox('Growth Threshold (%):', [30, 50])
small_cap = st.sidebar.checkbox('Small Cap Only?', value=True)

# Ensure only one ticker is processed
st.sidebar.write(f"Selected ticker: {selected_ticker}")

# Function to fetch additional information about the chosen ticker
def fetch_additional_info(ticker):
    api_url = f'https://smallcapscoutupdate-196636255726.europe-west1.run.app/info?ticker={ticker}'
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch additional info for {ticker}. Response code: {response.status_code}")
        return None

# Fetch additional information for the selected ticker
additional_info = fetch_additional_info(selected_ticker)

# Display additional information if available
if additional_info:
    st.subheader("Additional Information about the Chosen Ticker and Its Last Status in the Stock Market")
    st.write(f"**Company Name:** {additional_info['Company name']}")
    st.write(f"**Market Cap:** ${additional_info['Market cap'] / 1_000_000:.2f} million USD")  # Market cap in millions
    st.write(f"**Revenues:** ${additional_info['Revenues']:.2f} USD")
    st.write(f"**Gross Profit:** ${additional_info['Gross Profit']:.2f} USD")
    st.write(f"**Net Income:** ${additional_info['Net Income']:.2f} USD")
    st.write(f"**Operating Cash Flows:** ${additional_info['Operating Cash Flows']:.2f} USD")

# Fetch performance and predictions from the external service
if selected_ticker:
    st.write(f"Displaying {model_choice.upper()} model predictions for ticker: {selected_ticker}")

    # API URL
    api_url = 'https://smallcapscoutupdate-196636255726.europe-west1.run.app/predict'

    # Parameters for the FastAPI request
    params = {
        'ticker': selected_ticker,
        'model_type': model_choice,  # API expects lowercase model type
        'quarter': selected_quarter,  # The selected quarter
        'horizon': horizon,  # Prediction horizon
        'threshold': f"{growth_threshold}%",  # Growth threshold as a percentage
        'small_cap': str(small_cap).lower()  # Convert boolean to lowercase string ('true'/'false')
    }

    # Send the request to the FastAPI endpoint
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Display the API response
        st.write(f"**Ticker:** {data['ticker']}")
        st.write(f"**Model Type:** {data['model_type']}")
        
        # Display prediction and worthiness
        worthiness = data.get('worthiness', 'No data available')
        st.subheader("Prediction")
        st.write(f"**Worthiness:** {worthiness}")

        # Display a fun message based on worthiness
        if worthiness.lower() == "not worthy":
            st.write("Based on our deep analytics, this stock might not be the best pick. Consider other options!")
        elif worthiness.lower() == "worthy":
            st.write("Congratulations! This stock is worthy according to our analysis. It might be a great investment!")
    else:
        st.error(f"Failed to fetch prediction data for {selected_ticker}. Response code: {response.status_code}")

# Additional professional feature: Suggested Resources
st.subheader("Suggested Resources for Further Analysis")
st.write("Check out the following resources to enhance your investment strategies:")
st.write("- [Yahoo Finance](https://finance.yahoo.com): Comprehensive stock market data.")
st.write("- [MarketWatch](https://www.marketwatch.com): Up-to-date financial news and analysis.")
st.write("- [Investopedia](https://www.investopedia.com): Learn more about financial concepts.")

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
