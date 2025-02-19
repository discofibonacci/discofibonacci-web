from flask import Flask, jsonify, request
import yfinance as yf
import requests

app = Flask(__name__)
@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200  # Health check returns a 200 OK

# Liquidity & Order Flow Tracking
def get_order_flow(symbol):
    url = f"https://finnhub.io/api/v1/stock/orderbook?symbol={symbol}&token=YOUR_API_KEY"
    response = requests.get(url).json()
    return response

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
