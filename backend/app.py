from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import yfinance as yf
import numpy as np

app = Flask(__name__)

# Allow CORS from all origins (update to specific origins later if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/market-data', methods=['GET'])
def get_market_data():
    symbol = request.args.get('symbol', 'AAPL').upper()  # Ensure symbol is uppercase
    
    try:
    ticker = yf.Ticker(symbol)  # Ensure this line is present!
    hist = ticker.history(period="1d", interval="5m")

    # Debugging: Check if Yahoo Finance returned empty data
    if hist.empty:
        print(f"Yahoo Finance returned empty data for {symbol}. Full response: {ticker.history_metadata}")
        return jsonify({"error": f"No price data found for {symbol}. Response: {ticker.history_metadata}"}), 404
except Exception as e:
    print(f"Error fetching data for {symbol}: {str(e)}")
    return jsonify({"error": f"Failed to get ticker '{symbol}' reason: {str(e)}"}), 500

        latest = hist.iloc[-1]  # Get latest price data

        # Compute RSI if we have enough data points
        if len(hist['Close']) > 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = round(rsi.iloc[-1], 2)
        else:
            rsi_value = "Not enough data for RSI"

        data = {
            "symbol": symbol,
            "order_flow": {
                "open": round(latest['Open'], 4),
                "high": round(latest['High'], 4),
                "low": round(latest['Low'], 4),
                "close": round(latest['Close'], 4),
                "volume": int(latest['Volume'])
            },
            "support_level": "No Data Available",  # Placeholder for future support levels
            "rsi": rsi_value
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch data for {symbol}. Reason: {str(e)}"}), 500


@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
