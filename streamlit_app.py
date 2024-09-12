import streamlit as st
import pandas as pd
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
st.sidebar.image("images/logo1.png", width=170)  # Ensure logo is in the "images" folder

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

# Step 2: Conditionally display the quarter range slider for models other than RNN
if model_choice != 'RNN':
    def quarter_range_slider():
        quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4']]
        quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
        return st.sidebar.select_slider('Select a quarter range:', options=quarter_labels, value=('2010-Q1', '2024-Q4'))

    from_quarter, to_quarter = quarter_range_slider()
else:
    from_quarter, to_quarter = None, None  # If RNN is selected, we don't use quarter ranges

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
        'limit': 5  # Adjust this limit as needed
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

# Fetch performance and predictions from the external FastAPI service
if tickers:
    st.write(f"Displaying {model_choice} model predictions for tickers: {', '.join(tickers)}")
    
    for ticker in tickers:
        api_url = f'https://smallcapscout-196636255726.europe-west1.run.app/predict'
        params = {
            'ticker': ticker,
            'model_type': model_choice.lower().replace(" ", "_"),
            'quarter': to_quarter if to_quarter else "2023-Q2",
            'sequence': 4,
            'horizon': 'year-ahead',
            'threshold': '50%25',
            'small_cap': 'True'
        }
        
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Displaying the fetched data from FastAPI
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
            st.write(f"Failed to fetch data for {ticker}. Response code: {response.status_code}")
            st.error("Failed to fetch data from the external service.")

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
