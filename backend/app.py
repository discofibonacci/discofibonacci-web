import os
import time
import requests
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://discofibonacci-web.onrender.com"}})

# API Keys
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200

# Alpha Vantage - Order Flow Tracking
def get_order_flow(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        time.sleep(12)  # Prevent Alpha Vantage rate limits
        response = requests.get(url)
        response_json = response.json()

        if "Time Series (5min)" in response_json:
            latest_timestamp = max(response_json["Time Series (5min)"].keys())
            latest_data = response_json["Time Series (5min)"][latest_timestamp]
            return {
                "open": latest_data["1. open"],
                "high": latest_data["2. high"],
                "low": latest_data["3. low"],
                "close": latest_data["4. close"],
                "volume": latest_data["5. volume"]
            }

        print(f"⚠️ No valid order flow data found for {symbol}")
        return {"error": "No valid order flow data found."}

    except Exception as e:
        print(f"❌ Alpha Vantage API Error for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch order flow: {str(e)}"}

# Yahoo Finance - Support Level Detection
def get_support_levels(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="6mo")

        if data.empty:
            print(f"⚠️ {symbol}: No price data found for support levels (6mo).")
            return "No Data Available"

        min_support = round(min(data["Low"]), 2)
        print(f"✅ Support level for {symbol}: {min_support}")
        return min_support

    except Exception as e:
        print(f"❌ Yahoo Finance Error for {symbol}: {str(e)}")
        return "Error Fetching Data"

# Yahoo Finance - RSI Calculation
def get_rsi(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3mo")  # Use 3-month data for better accuracy

        if data.empty or "Close" not in data.columns:
            print(f"⚠️ {symbol}: No price data found for RSI (3mo).")
            return "No Data Available"

        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        if rsi.isna().iloc[-1]:
            print(f"⚠️ {symbol}: RSI calculation resulted in NaN!")
            return "Error"

        rsi_value = round(rsi.iloc[-1], 2)
        print(f"✅ RSI for {symbol}: {rsi_value}")
        return rsi_value

    except Exception as e:
        print(f"❌ Yahoo Finance Error for {symbol}: {str(e)}")
        return "Error Fetching Data"

@app.route("/market-data", methods=["GET"])
def market_data():
    symbol = request.args.get("symbol", "AAPL")
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
    port = int(os.environ.get("PORT", 10000))  # Ensure correct port binding for Render
    app.run(host="0.0.0.0", port=port)
