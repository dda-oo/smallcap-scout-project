# Stock Analysis and Prediction Dashboard

## Introduction

Welcome to the **Stock Analysis and Prediction Dashboard**! This application is designed to provide users with valuable insights into stock performance and future growth predictions for individual stock tickers. This project serves as the front end of the [Small-Cap Scout backend repository](https://github.com/cnance09/Small-Cap-Scout).

## Project Overview

### Objectives

- **Finds small-cap US companies** with a high likelihood of extraordinary returns based on fundamentals.
- **Employs the latest machine learning** and neural network techniques to identify high-performing stocks.
- **Provides insights** for individual and professional investors.
- **Forecast Stock Performance:** Predict value growth at quarter-ahead, year-ahead, and two-year horizons.
- **Dynamic User Interface:** Investors can customize model inputs.
- **Investment Recommendations:** Probability of success reported for each stock, helping users understand historical expectations and analyze past market trends.

## Key Features

- **SEC Edgar Financial Statements (2009 - Q2 2024):** Financial data of US companies (optional extension).
- **Marketaux API:** Real-time stock news and company insights.
- **Yahoo Finance API:** Historical stock pricing and performance data.
- **Google Trends & Sentiment Analysis:** To capture market sentiment.
- **Economic Data & Trade Flows:** FRED, CME, MIT Observatory.

## Aspects of the Custom-Built Dataset

- **Data Size:** Over 170k observations from more than 5,800 companies with 59 features.
- **Models Employed:**
  - **Baseline:**
    - Logistic Regression: Classification tasks for predicting company growth.
    - KNN (K-Nearest Neighbors): Classify stocks based on features of k-neighbors.
  - **Main Model:**
    - XG Boost: Cross-sectional predictions on future growth.
    - RNN (Recurrent Neural Networks): Time-series predictions for future growth.

### Parameters for Prediction

- **TICKER:** Stock symbol
- **Model Type:** XG Boost & Recurrent Neural Network (xgb | rnn)
- **Quarter:** Quarter of prediction (e.g., 2024-Q2)
- **Horizon:** Time horizon of prediction (quarter-ahead, year-ahead, two-years-ahead)
- **Threshold:** Growth percentage threshold for ‘successful’ companies (30% | 50%)
- **Small Cap:** Whether to only consider small companies (True | False)

### Output & Performance

- **Output Predictions:** 
  - **Horizon:** quarter-ahead, year-ahead, two-years-ahead
  - **Threshold:** 50% growth
  - **Accuracy:** 72%
  - **Precision:** 65%
  
Additional features include sentiment data, news analysis, and trade flows. Further improvements could involve automating the process to schedule periodic updates using Prefect.

## How to Use

To get started, simply select your desired ticker, model, and parameters in the sidebar. View the predictions along with relevant financial metrics and explore additional resources for further analysis to make more informed investment decisions.

## Disclaimer

Please note that this project is for educational purposes only. The predictions and information provided here are not financial advice. Consult a professional financial advisor for investment decisions.

## Final Note

Thank you for using the Stock Analysis and Prediction Dashboard. We hope this tool enhances your understanding of stock market dynamics and assists you in your investment journey.
