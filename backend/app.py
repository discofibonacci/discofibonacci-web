import os
import yfinance as yf
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/market-data', methods=['GET'])
def get_market_data():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({"error": "Symbol parameter is required."}), 400

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            return jsonify({"error": f"No price data found for {symbol}."}), 404
        
        latest = hist.iloc[-1]
        
        if len(hist['Close']) > 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = None
        
        pivot = (latest["High"] + latest["Low"] + latest["Close"]) / 3
        resistance_1 = (2 * pivot) - latest["Low"]
        support_1 = (2 * pivot) - latest["High"]
        resistance_2 = pivot + (latest["High"] - latest["Low"])
        support_2 = pivot - (latest["High"] - latest["Low"])

        return jsonify({
            "symbol": symbol,
            "order_flow": {
                "close": round(latest['Close'], 2),
                "high": round(latest['High'], 2),
                "low": round(latest['Low'], 2),
                "open": round(latest['Open'], 2),
                "volume": int(latest['Volume'])
            },
            "rsi": None if rsi is None else round(rsi.iloc[-1], 2),
            "support_level": [round(support_1, 2), round(support_2, 2)],
            "resistance_level": [round(resistance_1, 2), round(resistance_2, 2)]
        })

    except Exception as e:
        return jsonify({"error": f"Failed to get ticker '{symbol}' reason: {str(e)}"}), 500

@app.route('/market-depth', methods=['GET'])
def get_market_depth():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({"error": "Symbol parameter is required."}), 400
    
    try:
        base_price = np.random.uniform(240, 250)  # Simulated base price variation
        order_book = [
            {"symbol": symbol, "price": round(base_price * np.random.uniform(0.99, 1.01), 2), "size": np.random.randint(100, 1000), "type": "bid", "liquidity": round(np.random.random(), 2)},
            {"symbol": symbol, "price": round(base_price * np.random.uniform(1.01, 1.02), 2), "size": np.random.randint(100, 1000), "type": "ask", "liquidity": round(np.random.random(), 2)},
            {"symbol": symbol, "price": round(base_price * np.random.uniform(0.98, 1.00), 2), "size": np.random.randint(100, 1000), "type": "bid", "liquidity": round(np.random.random(), 2)},
            {"symbol": symbol, "price": round(base_price * np.random.uniform(1.02, 1.03), 2), "size": np.random.randint(100, 1000), "type": "ask", "liquidity": round(np.random.random(), 2)}
        ]

        return jsonify(order_book)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
