from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# ✅ Define Flask app first
app = Flask(__name__)

# ✅ Apply CORS properly (Allow only the GitHub Pages frontend)
CORS(app, resources={r"/*": {"origins": "https://discofibonacci.github.io"}})

@app.route("/healthz")
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/alert", methods=["POST"])
def send_alert():
    data = request.json
    print("Received alert:", data)
    return jsonify({"status": "success"}), 200

@app.route("/")
def home():
    return jsonify({"message": "Market Maker Sniper API is live!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default port to 10000
    app.run(host="0.0.0.0", port=port, debug=False)
