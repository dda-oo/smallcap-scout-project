import streamlit as st
import requests
import pandas as pd

# Title and description
st.title("Stock Performance and Prediction Dashboard")
st.write("""
    Enter one or more stock tickers to analyze their performance, predict future trends, 
    and receive an investment recommendation. All predictions are handled by our external prediction service.
""")

# Step 1: Select the range of years
years_range = st.slider('Which years are you interested in?', 2010, 2024, (2010, 2024))

# Step 2: Enter the tickers
tickers = st.text_input('Enter up to 4 tickers separated by commas (e.g., AAPL, TSLA, AMZN):', 'AAPL, TSLA')

# Limit the number of tickers to a maximum of 4
tickers = [ticker.strip().upper() for ticker in tickers.split(',')][:4]

# If tickers are provided, proceed with API request to external page
if tickers:
    st.write(f"Processing predictions for: {', '.join(tickers)}")

    # Prepare the data for the request
    ticker_string = ','.join(tickers)
    years_start, years_end = years_range

    # Make a request to the external prediction service
    url = "https://smallcapscout-196636255726.europe-west1.run.app/predict"
    params = {
        'tickers': ticker_string,
        'start_year': years_start,
        'end_year': years_end
    }

    try:
        # Send GET request to external page and get response
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful

        # Assuming the external page returns a JSON with 'predictions' and 'recommendations'
        result = response.json()

        # Display predictions
        st.write("### Predictions")
        for prediction in result['predictions']:
            ticker = prediction['ticker']
            st.write(f"**{ticker}**:")
            df = pd.DataFrame(prediction['data'])
            st.line_chart(df)

        # Display investment recommendations
        st.write("### Investment Recommendations")
        for recommendation in result['recommendations']:
            ticker = recommendation['ticker']
            st.write(f"**{ticker}:** {recommendation['advice']}")

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the external service: {e}")

# Step 3: Embedding the external prediction service as an iframe
st.write("### Full Prediction Service")
st.components.v1.html(
    """
    <iframe src="https://smallcapscout-196636255726.europe-west1.run.app/predict" width="100%" height="600" frameborder="0">
    </iframe>
    """,
    height=600,
)
