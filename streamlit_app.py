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
    tickers_df = pd.read_csv('data/cik_ticker_pairs.csv')  # Ensure this path is correct
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
        # Limit to September 2024 (Q3 of 2024)
        quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4'] if not (y == 2024 and q == 'Q4')]
        quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
        return st.sidebar.select_slider('Select a quarter range:', options=quarter_labels, value=('2010-Q1', '2024-Q3'))

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

# Step 4: Define additional parameters for the FastAPI request
sequence = st.sidebar.slider('Select Sequence Length:', min_value=1, max_value=12, value=4)
horizon = st.sidebar.selectbox('Select Prediction Horizon:', ['quarter-ahead', 'year-ahead', '2_year-ahead'])
threshold = st.sidebar.slider('Select Threshold:', min_value=0.1, max_value=1.0, step=0.1, value=0.5)
small_cap = st.sidebar.checkbox('Small Cap Only?', value=True)

# Fetch news for the selected tickers from the Marketaux API
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
    st.write(f"Displaying {model_choice} model predictions for tickers: {', '.join(tickers)}")
    
    # Iterate through each selected ticker
    for ticker in tickers:
        api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
        params = {
            'ticker': ticker,  # Use 'ticker' (singular) as required by your API
            'model_type': model_choice.lower().replace(' ', '_'),  # API expects lowercase and underscore-separated model types
            'quarter': to_quarter if to_quarter else '2024-Q3',  # Default to '2024-Q3' if quarter range is not set (RNN)
            'sequence': sequence,
            'horizon': horizon,
            'threshold': f"{int(threshold * 100)}%",  # Convert to percentage
            'small_cap': str(small_cap).lower()  # Ensure it's lowercase true/false for the API
        }
        
        # Send the request for each ticker
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            predictions = data.get('predictions', [])
            recommendations = data.get('recommendations', [])

            # If the model is RNN, show only predictions
            if model_choice == 'RNN':
                st.write(f"### Predictions for {ticker}")
                for year in ['quarter_ahead', 'year_ahead', '2_year_ahead']:
                    st.write(f"{year}: {data['predictions'][0]['data'].get(year)}")
            else:
                # Display historical performance and predictions
                ticker_data = pd.DataFrame(data['predictions'][0]['data'])
                st.write(f"Performance for {ticker}:")
                st.line_chart(ticker_data)

                # Display predictions
                st.write(f"### Predictions for {ticker}")
                for year in ['quarter_ahead', 'year_ahead', '2_year_ahead']:
                    st.write(f"{year}: {data['predictions'][0]['data'].get(year)}")

            # Display investment recommendations
            st.write(f"### Investment Recommendations for {ticker}")
            for recommendation in recommendations:
                advice = recommendation['advice']
                st.write(f"**{ticker}:** {advice}")
        else:
            st.error(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")

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


#####################################

# Debugging/Test Section for FastAPI Connection
st.header("Test FastAPI Connection")

# Input for ticker and model (basic test inputs)
test_ticker = st.text_input("Enter ticker to test (e.g., AAPL):", "AAPL")
test_model = st.selectbox('Choose a model for testing:', ['RNN', 'KNN', 'Logistic Regression'])
test_quarter = st.text_input("Enter quarter (e.g., 2024-Q2):", "2024-Q2")
test_sequence = st.slider('Select Sequence Length for testing:', min_value=1, max_value=12, value=4)
test_horizon = st.selectbox('Select Prediction Horizon for testing:', ['quarter-ahead', 'year-ahead', '2_year-ahead'])
test_threshold = st.slider('Select Threshold for testing:', min_value=0.1, max_value=1.0, step=0.1, value=0.5)
test_small_cap = st.checkbox('Small Cap Only?', value=True)

# Button to trigger the test API call
if st.button("Test API Call"):
    api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
    params = {
        'ticker': test_ticker,
        'model_type': test_model.lower().replace(' ', '_'),  # API expects lowercase and underscore-separated model types
        'quarter': test_quarter,
        'sequence': test_sequence,
        'horizon': test_horizon,
        'threshold': f"{int(test_threshold * 100)}%",  # Convert to percentage
        'small_cap': str(test_small_cap).lower()  # Ensure it's lowercase true/false for the API
    }
    
    # Fetch data from the API
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        st.write("### Raw API Response")
        st.json(data)  # Display the raw JSON data from the API
    else:
        st.error(f"API request failed with status code: {response.status_code}")

