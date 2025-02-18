from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/")
def home():
    return "Backend is running!"

# ✅ ADD A HEALTH CHECK ROUTE FOR RENDER
@app.route("/healthz")
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/alert", methods=["POST"])
def alert():
    data = request.json
    print(f"Received alert: {data['message']}")
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    from waitress import serve  # Production WSGI server
    serve(app, host="0.0.0.0", port=10000)  # Bind to 10000

