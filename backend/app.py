import os
import requests
import yfinance as yf
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://discofibonacci.github.io", "https://discofibonacci-web.onrender.com"]}})

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

# Liquidity & Order Flow Tracking
def get_order_flow(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url).json()
        
        # Debugging: Print full response in logs
        print(f"🔍 API Response for {symbol}: {response}")

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
            print(f"⚠️ No 'Time Series (5min)' data found in API response for {symbol}")
            return {"error": "No valid order flow data found."}
    
    except Exception as e:
        print(f"❌ Error fetching order flow for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch order flow: {str(e)}"}

# Optimized Support Level Detection (3-month period)
def get_support_levels(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="6mo")

        if data.empty:
            print(f"⚠️ {symbol}: No price data found for support levels (6mo).")
            return "No Data Available"

        return round(min(data['Low']), 2)

    except Exception as e:
        print(f"❌ Yahoo Finance Error for {symbol}: {str(e)}")
        return "Error Fetching Data"

def get_rsi(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3mo")  # ✅ Adjusted timeframe

        if data.empty:
            print(f"⚠️ {symbol}: No price data found for RSI (3mo).")
            return "No Data Available"

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        if rsi.isna().iloc[-1]:
            return "Error"

        return round(rsi.iloc[-1], 2)

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

# Ensure correct port binding for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
