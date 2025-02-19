import os
import requests
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://discofibonacci.github.io"}})

# ✅ Correct Placement: Health Check Route
@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200  # Health check returns a 200 OK

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Liquidity & Order Flow Tracking
def get_order_flow(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url).json()
        if "Time Series (5min)" in response:
            latest_timestamp = max(response["Time Series (5min)"].keys())
            latest_data = response["Time Series (5min)"][latest_timestamp]
            return {
                "open": latest_data["1. open"],
                "high": latest_data["2. high"],
                "low": latest_data["3. low"],
                "close": latest_data["4. close"],
                "volume": latest_data["5. volume"]
            }
        else:
            return {"error": "No valid order flow data found."}
    except Exception as e:
        return {"error": f"Failed to fetch order flow: {str(e)}"}

# Support Level Detection
def get_support_levels(symbol):
    try:
        data = yf.Ticker(symbol).history(period="6mo")
        
        # Debugging: Log data retrieval
        if data.empty:
            print(f"⚠️ {symbol}: Yahoo Finance returned an empty dataset!")
            return "No Data Available"
        
        if 'Low' not in data.columns:
            print(f"⚠️ {symbol}: 'Low' price data is missing from the dataset!")
            return "No Data Available"

        # Extract the lowest price as support level
        support_level = round(min(data['Low']), 2)
        return support_level
    
    except Exception as e:
        print(f"❌ Error fetching support levels for {symbol}: {str(e)}")
        return "Error Fetching Data"

# RSI Momentum Indicator
def get_rsi(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1mo")
        
        if data.empty or 'Close' not in data.columns:
            print(f"⚠️ {symbol}: No 'Close' price data found for RSI calculation!")
            return "No Data Available"

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Ensure RSI is not NaN
        if rsi.isna().iloc[-1]:
            print(f"⚠️ {symbol}: RSI calculation resulted in NaN!")
            return "No Data Available"

        return round(rsi.iloc[-1], 2)

    except Exception as e:
        print(f"❌ Error fetching RSI for {symbol}: {str(e)}")
        return "Error Fetching Data"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Ensures correct port binding for Render
    app.run(host="0.0.0.0", port=port)
