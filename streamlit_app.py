import streamlit as st
import pandas as pd
import requests

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

# Load available tickers dynamically from a CSV file
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
def quarter_range_slider():
    # Limit to September 2024 (Q3 of 2024)
    quarters = [(y, q) for y in range(2010, 2025) for q in ['Q1', 'Q2', 'Q3', 'Q4'] if not (y == 2024 and q == 'Q4')]
    quarter_labels = [f"{year}-{quarter}" for year, quarter in quarters]
    return st.sidebar.select_slider('Select a quarter range:', options=quarter_labels, value=('2010-Q1', '2024-Q3'))

if model_choice != 'RNN':
    from_quarter, to_quarter = quarter_range_slider()
else:
    from_quarter, to_quarter = None, None  # If RNN is selected, we don't use quarter ranges

# Step 3: Select tickers dynamically using a multiselect box in the sidebar
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

# Fetch performance and predictions for each ticker
if tickers:
    for ticker in tickers:
        st.write(f"Displaying {model_choice} model predictions for {ticker}")

        # Construct the API request URL
        api_url = 'https://smallcapscout-196636255726.europe-west1.run.app/predict'
        params = {
            'ticker': ticker,  # Send ticker one by one
            'model_type': model_choice.lower().replace(' ', '_'),  # API expects lowercase and underscore-separated model types
            'quarter': to_quarter if to_quarter else '2024-Q3',  # Default to '2024-Q3' if quarter range is not set (RNN)
            'sequence': sequence,
            'horizon': horizon,
            'threshold': f"{int(threshold * 100)}%",  # Convert to percentage
            'small_cap': small_cap
        }

        # Send the GET request to the FastAPI backend
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Display the prediction and related information
            st.write(f"### Ticker: {data['ticker']}")
            st.write(f"**Model Type:** {data['model_type']}")
            st.write(f"**Quarter:** {data['quarter']}")
            st.write(f"**Sequence:** {data['sequence']}")
            st.write(f"**Horizon:** {data['horizon']}")
            st.write(f"**Threshold:** {data['threshold']}")
            st.write(f"**Small Cap:** {data['small_cap']}")
            st.write(f"**Prediction:** {data['prediction']} (1 = Worthy, 0 = Not Worthy)")
            st.write(f"**Worthiness:** {data['worthiness']}")

        else:
            st.write(f"Failed to fetch data for {ticker}. Response code: {response.status_code}")
            st.error("Failed to fetch data from the external service.")

# Disclaimer at the bottom of the sidebar or main page
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
