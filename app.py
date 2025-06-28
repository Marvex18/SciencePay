from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import random
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock database
users_db = {
    "test@example.com": {
        "password": "password123",
        "balance": 1500.00,
        "transactions": [
            {
                "id": f"TX{int(time.time())}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": "Initial bonus",
                "amount": 1500.00,
                "status": "completed",
                "type": "bonus"
            }
        ]
    }
}

articles_db = [
    {
        "id": 1,
        "title": "The Future of Quantum Computing",
        "source": "Science Journal",
        "excerpt": "Exploring the potential of quantum computers to revolutionize industries from medicine to cryptography.",
        "image": "https://source.unsplash.com/random/600x400/?quantum",
        "reward": 50,
        "content": "<p>Quantum computing represents a fundamental shift from traditional computing...</p>"
    },
    {
        "id": 2,
        "title": "CRISPR Gene Editing Breakthrough",
        "source": "Nature Biology",
        "excerpt": "New advancements in CRISPR technology allow for more precise genetic modifications with fewer off-target effects.",
        "image": "https://source.unsplash.com/random/600x400/?dna",
        "reward": 45,
        "content": "<p>CRISPR-Cas9 has revolutionized genetic engineering since its discovery...</p>"
    }
]

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # For demo purposes, accept any credentials and create account if not exists
    if email not in users_db:
        users_db[email] = {
            "password": password,
            "balance": 500.00,  # Starting bonus
            "transactions": [
                {
                    "id": f"TX{int(time.time())}",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": "Welcome bonus",
                    "amount": 500.00,
                    "status": "completed",
                    "type": "bonus"
                }
            ]
        }
    
    return jsonify({
        "success": True,
        "user": {
            "email": email,
            "balance": users_db[email]["balance"]
        }
    })

@app.route('/api/articles', methods=['GET'])
def get_articles():
    return jsonify({
        "success": True,
        "articles": articles_db
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    email = request.args.get('email')
    if email not in users_db:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    return jsonify({
        "success": True,
        "transactions": users_db[email]["transactions"]
    })

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    email = data.get('email')
    amount = float(data.get('amount'))
    bank_name = data.get('bank_name')
    account_number = data.get('account_number')
    account_name = data.get('account_name')
    
    if email not in users_db:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    if amount > users_db[email]["balance"]:
        return jsonify({"success": False, "message": "Insufficient balance"}), 400
    
    # Create pending transaction
    transaction_id = f"TX{int(time.time())}"
    new_transaction = {
        "id": transaction_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": f"Withdrawal to {bank_name}",
        "amount": -amount,
        "status": "pending",
        "type": "withdrawal"
    }
    
    users_db[email]["transactions"].insert(0, new_transaction)
    
    # In a real app, you would initiate the bank transfer here
    # For demo, we'll simulate processing
    
    return jsonify({
        "success": True,
        "transaction_id": transaction_id,
        "new_balance": users_db[email]["balance"] - amount
    })

@app.route('/api/complete-article', methods=['POST'])
def complete_article():
    data = request.get_json()
    email = data.get('email')
    article_id = data.get('article_id')
    
    if email not in users_db:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    article = next((a for a in articles_db if a["id"] == article_id), None)
    if not article:
        return jsonify({"success": False, "message": "Article not found"}), 404
    
    # Add reward to balance
    reward = article["reward"]
    users_db[email]["balance"] += reward
    
    # Create transaction
    transaction_id = f"TX{int(time.time())}"
    new_transaction = {
        "id": transaction_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": f"Article: {article['title']}",
        "amount": reward,
        "status": "completed",
        "type": "earning"
    }
    
    users_db[email]["transactions"].insert(0, new_transaction)
    
    return jsonify({
        "success": True,
        "reward": reward,
        "new_balance": users_db[email]["balance"],
        "transaction_id": transaction_id
    })

if __name__ == '__main__':
    app.run(debug=True)
