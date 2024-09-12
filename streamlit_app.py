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
