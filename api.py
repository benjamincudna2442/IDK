from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import json_util
import re

app = Flask(__name__)

# MongoDB configuration (same as in the Telegram bot)
MONGO_URI = "mongodb+srv://ytpremium4434360:zxx1VPDzGW96Nxm3@itssmarttoolbot.dhsl4.mongodb.net/?retryWrites=true&w=majority&appName=ItsSmartToolBot"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["SangmataBot"]
history_collection = db["user_history"]

def get_history_by_user(user):
    """
    Retrieve user history by user_id or username.
    If user is numeric, treat as user_id; otherwise, treat as username (without @).
    """
    # Remove @ if present in username
    user = user.lstrip('@')
    
    # Check if the input is a numeric user_id
    if user.isdigit():
        query = {"user_id": int(user)}
    else:
        query = {"username": user}
    
    # Fetch entries from MongoDB, sorted by timestamp descending
    entries = list(history_collection.find(query).sort("timestamp", -1))
    
    if not entries:
        return None
    
    # Format response similar to the Telegram bot
    names, usernames = [], []
    for entry in entries:
        # Avoid duplicate names
        if entry['name'] not in [n.split("] ", 1)[-1] for n in names]:
            names.append(f"[{entry['timestamp']}] {entry['name']}")
        # Avoid duplicate usernames, only include non-None usernames
        if entry['username'] != "None" and entry['username'] not in [u.split("] @", 1)[-1] for u in usernames]:
            usernames.append(f"[{entry['timestamp']}] @{entry['username']}")
    
    # Prepare response
    response = {
        "user_id": entries[0]["user_id"],
        "names": [f"{i+1:02d}. {n}" for i, n in enumerate(names)],
        "usernames": [f"{i+1:02d}. {u}" for i, u in enumerate(usernames)]
    }
    return response

@app.route('/usersdb', methods=['GET'])
def usersdb():
    user = request.args.get('user')
    
    if not user:
        return jsonify({"error": "Missing 'user' parameter. Provide user_id or username."}), 400
    
    history = get_history_by_user(user)
    
    if not history:
        return jsonify({"error": "No history found for the provided user."}), 404
    
    return jsonify(history), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)