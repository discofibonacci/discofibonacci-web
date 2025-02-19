from flask import Flask, jsonify, request
import yfinance as yf
import requests

app = Flask(__name__)
@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200  # Health check returns a 200 OK

# Liquidity & Order Flow Tracking
import os

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"

    
    try:
        response = requests.get(url).json()
        if "Time Series (5min)" in response:
            latest_timestamp = max(response["Time Series (5min)"].keys())  # Get the most recent data point
            latest_data = response["Time Series (5min)"][latest_timestamp]
            
            order_flow = {
                "open": latest_data["1. open"],
                "high": latest_data["2. high"],
                "low": latest_data["3. low"],
                "close": latest_data["4. close"],
                "volume": latest_data["5. volume"]
            }
            return order_flow
        else:
            return {"error": "No valid order flow data found."}
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
    data = yf.Ticker(symbol).history(period="1mo")
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

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
