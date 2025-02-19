import os
import requests
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://discofibonacci.github.io"}})

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200  # Health check returns a 200 OK

# Liquidity & Order Flow Tracking
def get_order_flow(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()  # Ensure we get a JSON response

        if "Time Series (5min)" not in data:
            return {"error": "No valid order flow data found."}

        latest_timestamp = max(data["Time Series (5min)"].keys())  # Get the latest time point
        latest_data = data["Time Series (5min)"][latest_timestamp]

        order_flow = {
            "open": latest_data.get("1. open", "N/A"),
            "high": latest_data.get("2. high", "N/A"),
            "low": latest_data.get("3. low", "N/A"),
            "close": latest_data.get("4. close", "N/A"),
            "volume": latest_data.get("5. volume", "N/A")
        }

        return order_flow

    except Exception as e:
        return {"error": f"Failed to fetch order flow: {str(e)}"}

# Support Level Detection
def get_support_levels(symbol):
    try:
        data = yf.Ticker(symbol).history(period="6mo")

        if data.empty or 'Low' not in data.columns:
            print(f"{symbol}: No price data found, returning default support level")
            return "No Data Available"

        support_level = min(data['Low'])
        return round(support_level, 2)

    except Exception as e:
        print(f"Failed to get ticker '{symbol}' reason: {str(e)}")
        return "Error Fetching Data"

# RSI Momentum Indicator
def get_rsi(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1mo")
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    except Exception as e:
        return f"Error calculating RSI: {str(e)}"

@app.route("/market-data", methods=["GET"])
def market_data():
    symbol = request.args.get("symbol", "AAPL")  # Default to AAPL if no symbol is given
    order_flow = get_order_flow(symbol)
    support_level = get_support_levels(symbol)
    rsi = get_rsi(symbol)

    return jsonify({
        "symbol": symbol,
        "order_flow": order_flow,
        "support_level": support_level,
        "rsi": rsi
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
