from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import bcrypt
import os

from chat import Chatbot  # ✅ Import the class

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("PeriChat")
users_collection = db.get_collection("users")

# ✅ Initialize chatbot instance
bot = Chatbot()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signin", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    confirm = data.get("confirm_password")

    if not all([name, email, password, confirm]):
        return jsonify({"error": "Please fill in all fields."}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match."}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists."}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = {"name": name, "email": email, "password": hashed_pw}
    users_collection.insert_one(user)
    return jsonify({"message": "User created successfully."})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    name = data.get("username")
    password = data.get("password")

    if not name or not password:
        return jsonify({"error": "Missing username or password."}), 400

    user = users_collection.find_one({"name": name})
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.get("password")):
        return jsonify({"error": "Invalid username or password."}), 401

    return jsonify({"message": "Login successful."})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"response": "Empty message received."}), 400
    try:
        response = bot.get_response(user_message)  # ✅ Call chatbot method
        return jsonify({"response": response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"response": "An error occurred on the server."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
