import streamlit as st
import pandas as pd
import requests
import json
import http.client
import urllib.parse

# Set the favicon and page title
st.set_page_config(
    page_title="Stock Analysis and Prediction Dashboard", 
    page_icon="images/favicon.ico",  
    layout="wide"  
)

# Sidebar layout for form inputs
st.sidebar.header("Customize Your Stock Analysis")

# Add the logo to the sidebar, resized and smaller
st.sidebar.image("images/logo2.png", width=170)

# Title and description (centered on the main page)
st.title("Stock Analysis and Prediction Dashboard")
st.write("""
    Welcome to the Stock Analysis and Prediction Dashboard, where we combine advanced data models to provide insightful 
    predictions on future stock performance. Analyze stock trends, select machine learning models, and get the latest 
    company financial data for informed decision-making.
""")

# Load available tickers dynamically from a CSV file
@st.cache
def load_tickers():
    tickers_df = pd.read_csv('data/cik_ticker_pairs.csv')  
    return tickers_df['Ticker'].tolist()

available_tickers = load_tickers()

# Step 1: Select a model from the dropdown (limited to rnn and xgb)
model_choice = st.sidebar.selectbox(
    'Choose a model for prediction:',
    ['rnn', 'xgb']  # Updated to lowercase as per request
)

# Step 2: Select a quarter (limited to 2024-Q2 as the latest quarter)
def quarter_range_slider():
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4'] if not (y == 2024 and q == 'Q3' or q == 'Q4')]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
    quarter_labels.reverse()  # Show latest first
    return st.sidebar.selectbox('Select a quarter:', options=quarter_labels, index=0)

selected_quarter = quarter_range_slider()

# Step 3: Select a single ticker
selected_ticker = st.sidebar.selectbox('Select a ticker:', available_tickers)

# Step 4: Additional parameters for the request (Updated Growth Threshold and added "two-years-ahead")
horizon = st.sidebar.selectbox('Select Prediction Horizon:', ['quarter-ahead', 'year-ahead', 'two-years-ahead'])
threshold = st.sidebar.selectbox('Growth Threshold (%):', [30, 50])
small_cap = st.sidebar.checkbox('Small Cap Only?', value=True)

st.sidebar.write(f"Selected ticker: {selected_ticker}")

# FastAPI URL and request to fetch predictions
if selected_ticker:
    st.write(f"Displaying {model_choice.upper()} model predictions for ticker: {selected_ticker}")
    
    api_url = 'https://smallcapscoutupdate-196636255726.europe-west1.run.app/predict'

    params = {
        'ticker': selected_ticker,
        'model_type': model_choice,  
        'quarter': selected_quarter,  
        'horizon': horizon,  
        'threshold': f"{threshold}%",  
        'small_cap': str(small_cap).lower()  
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Display only Ticker and Model Type in the prediction section
        st.write(f"**Ticker:** {data['ticker']}")
        st.write(f"**Model Type:** {data['model_type']}")

        # Fetch additional info for the selected ticker
        info_url = f"https://smallcapscoutupdate-196636255726.europe-west1.run.app/info?ticker={selected_ticker}"
        info_response = requests.get(info_url)

        if info_response.status_code == 200:
            info_data = info_response.json()
            st.write("### Additional Information on the Chosen Ticker: Latest Market Status")
            st.write(f"**Company name:** {info_data['Company name']}")
            st.write(f"**Market cap:** {info_data['Market cap']}")
            st.write(f"**Revenues:** {info_data['Revenues']}")
            st.write(f"**Gross Profit:** {info_data['Gross Profit']}")
            st.write(f"**Net Income:** {info_data['Net Income']}")
            st.write(f"**Operating Cash Flows:** {info_data['Operating Cash Flows']}")
        else:
            st.error(f"Failed to fetch additional information for {selected_ticker}")

        # Prediction and worthiness section
        st.write("### Prediction and Worthiness")
        worthiness = data.get('worthiness')
        if worthiness == 'worthy':
            st.write("Based on our deep analytics, this stock is deemed **worthy** for investment. 🚀")
        elif worthiness == 'not worthy':
            st.write("Based on our deep analytics, this stock is **not worthy** of investment at this time. 💼")
        else:
            st.error("Unexpected worthiness response.")

    else:
        st.error(f"Failed to fetch prediction data for {selected_ticker}. Response code: {response.status_code}")

# Fetch news for the selected ticker
def fetch_stock_news_marketaux(tickers):
    if not tickers:  
        return []

    conn = http.client.HTTPSConnection('api.marketaux.com')
    params = urllib.parse.urlencode({
        'api_token': 'ADMI4P1TMPl0bv5LUblXDRsitsoaRiLIfeFNNrlm',
        'symbols': ','.join(tickers),
        'limit': 5
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
