from flask import Flask, request, jsonify
from flask_cors import CORS
from app import ExpenseTracker

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

tracker = ExpenseTracker()

@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    category = data.get("category")
    amount = data.get("amount")
    if not category or not amount:
        return jsonify({"error": "Invalid input"}), 400
    tracker.add_expense(category, amount)
    return jsonify({"message": "Expense added successfully"}), 200

@app.route("/set_budget", methods=["POST"])
def set_budget():
    data = request.json
    category = data.get("category")
    month = data.get("month")
    monthly_budget = data.get("monthly_budget")
    if not category or not month or not monthly_budget:
        return jsonify({"error": "Invalid input"}), 400
    tracker.set_budget(category, month, monthly_budget)
    return jsonify({"message": "Budget set successfully"}), 200

@app.route("/reports", methods=["GET"])
def get_reports():
    month = request.args.get("month")
    if not month:
        return jsonify({"error": "Month is required"}), 400
    total_spending = tracker.get_total_spending(month)
    category_spending = tracker.get_category_spending(month)
    return jsonify({
        "total_spending": total_spending,
        "category_spending": [
            {"category": row["category"], "spending": row["spending"], "budget": row["monthly_budget"]}
            for row in category_spending
        ]
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
