import os
import requests
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)

# Correct CORS settings to allow both frontend & backend origins
CORS(app, resources={r"/*": {"origins": ["https://discofibonacci.github.io", "https://discofibonacci-web.onrender.com"]}})

# Alpha Vantage API Key from Render environment variables
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200  # Health check route

# 📊 Liquidity & Order Flow Tracking
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

# 🔻 Support Level Detection
def get_support_levels(symbol):
    try:
        data = yf.Ticker(symbol).history(period="3mo")  # 🔹 Use 3 months instead of 6

        print(f"🟡 Debugging Support Levels: Data for {symbol} → {data.tail()}")  # Debugging

        if data.empty or 'Low' not in data.columns:
            print(f"⚠️ No valid price data found for {symbol} (Support Level)")
            return "No Data Available"

        return round(min(data['Low']), 2)  # 🔹 Support based on 3-month lowest price
    except Exception as e:
        print(f"❌ Error fetching support levels for {symbol}: {str(e)}")
        return "Error Fetching Data"

# 📈 RSI Momentum Indicator
def get_rsi(symbol):
    try:
        data = yf.Ticker(symbol).history(period="14d")  # 🔹 Use 14-day window for faster RSI signals

        print(f"🟡 Debugging RSI: Data for {symbol} → {data.tail()}")  # Debugging

        if data.empty or 'Close' not in data.columns:
            print(f"⚠️ No valid closing price data for {symbol} (RSI Calculation)")
            return "No Data Available"

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(7).mean()  # 🔹 Faster 7-day rolling window
        loss = (-delta.where(delta < 0, 0)).rolling(7).mean()  # 🔹 Adjusted for momentum tracking
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        print(f"🔹 RSI Calculation for {symbol}: {rsi.dropna().tail()}")  # Debugging

        return round(rsi.iloc[-1], 2) if not rsi.isna().iloc[-1] else "No Data Available"
    except Exception as e:
        print(f"❌ Error fetching RSI for {symbol}: {str(e)}")
        return "Error Fetching Data"

# 🎯 API Endpoint for Market Data
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

# 🚀 Ensuring Proper Port Binding for Render Deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Bind correct port for Render
    app.run(host="0.0.0.0", port=port)
