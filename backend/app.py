import os
import yfinance as yf
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow CORS from all origins
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/market-data', methods=['GET'])
def get_market_data():
    symbol = request.args.get('symbol', 'AAPL').upper()

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="5m")

        if hist.empty:
            return jsonify({"error": f"No price data found for {symbol}."}), 404

        latest = hist.iloc[-1]

        # Calculate RSI
        if len(hist['Close']) > 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = None

        # Calculate VWAP
        hist['TypicalPrice'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
        hist['VWAP'] = (hist['TypicalPrice'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
        latest_vwap = round(hist['VWAP'].iloc[-1], 2)

        # Convert historical data into candlestick format
        candlesticks = hist[['Open', 'High', 'Low', 'Close']].reset_index()
        candlestick_data = candlesticks.tail(50).to_dict(orient="records")

        return jsonify({
            "order_flow": {
                "close": round(latest['Close'], 2),
                "high": round(latest['High'], 2),
                "low": round(latest['Low'], 2),
                "open": round(latest['Open'], 2),
                "volume": int(latest['Volume']),
                "vwap": latest_vwap
            },
            "rsi": None if rsi is None else round(rsi.iloc[-1], 2),
            "support_level": [round(latest['Low'] * 0.98, 2), round(latest['Low'] * 0.95, 2)],
            "resistance_level": [round(latest['High'] * 1.02, 2), round(latest['High'] * 1.05, 2)],
            "candlesticks": [
                {
                    "time": row['Datetime'].isoformat(),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2)
                }
                for _, row in candlesticks.tail(50).iterrows()
            ]
        })

    except Exception as e:
        return jsonify({"error": f"Failed to get ticker '{symbol}' reason: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
