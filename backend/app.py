import os
import yfinance as yf
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow CORS from all origins (update to specific origins later if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/market-data', methods=['GET'])
def get_market_data():
    symbol = request.args.get('symbol', 'AAPL').upper()  # Ensure symbol is uppercase

    try:
        ticker = yf.Ticker(symbol)  # Ensure this line is properly indented!
        hist = ticker.history(period="1d", interval="5m")

        # Debugging: Check if Yahoo Finance returned empty data
        if hist.empty:
            print(f"Yahoo Finance returned empty data for {symbol}. Full response: {ticker.history_metadata}")
            return jsonify({"error": f"No price data found for {symbol}. Response: {ticker.history_metadata}"}), 404

        latest = hist.iloc[-1]  # Get latest price data

        # Compute RSI if we have enough data points
        if len(hist['Close']) > 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = None

        return jsonify({
            "order_flow": {
                "close": latest['Close'],
                "high": latest['High'],
                "low": latest['Low'],
                "open": latest['Open'],
                "volume": latest['Volume']
            },
            "support_level": "No Data Available",
            "rsi": None if rsi is None else rsi.iloc[-1]
        })

    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return jsonify({"error": f"Failed to get ticker '{symbol}' reason: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
