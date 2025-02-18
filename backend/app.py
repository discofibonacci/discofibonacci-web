from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    print(f"Received alert: {data['message']}")
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Use environment variable PORT if available
    app.run(debug=True, host="0.0.0.0", port=port)  # Explicitly bind to port
