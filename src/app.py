"""
Smart Expense Tracker API

Endpoints:
  POST   /expenses                 Add a new expense
  GET    /expenses                 List all expenses (optional ?category=)
  GET    /expenses/<id>            Get a single expense
  DELETE /expenses/<id>            Delete an expense
  GET    /expenses/total           Total spend (overall + by category)
  GET    /expenses/summary/monthly Bonus: total spend grouped by month

Run directly with `python src/app.py`, or via the Flask CLI (see README).
"""

import os
import uuid
from collections import defaultdict

from flask import Flask, jsonify, request

from storage import ExpenseStore
from validation import ValidationError, validate_expense_payload


def create_app(data_file: str = None) -> Flask:
    app = Flask(__name__)

    data_file = data_file or os.environ.get("EXPENSES_FILE", "expenses.json")
    store = ExpenseStore(data_file)
    app.config["store"] = store  # exposed mainly so tests can reach it if needed

    # ---------- error handlers ----------

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"error": err.message}), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"error": "Not found"}), 404

    # ---------- routes ----------

    @app.route("/expenses", methods=["POST"])
    def add_expense():
        data = request.get_json(silent=True) or {}
        validate_expense_payload(data)

        expense = {
            "id": str(uuid.uuid4()),
            "title": data["title"].strip(),
            "amount": float(data["amount"]),
            "category": data["category"].strip(),
            "date": data["date"],
        }
        store.add(expense)
        return jsonify(expense), 201

    @app.route("/expenses", methods=["GET"])
    def list_expenses():
        category = request.args.get("category")
        if category:
            expenses = store.filter_by_category(category)
        else:
            expenses = store.all()
        return jsonify(expenses), 200

    @app.route("/expenses/total", methods=["GET"])
    def total_expenses():
        expenses = store.all()
        overall = round(sum(e["amount"] for e in expenses), 2)

        by_category = defaultdict(float)
        for e in expenses:
            by_category[e["category"]] += e["amount"]
        by_category = {k: round(v, 2) for k, v in by_category.items()}

        return jsonify({"overall_total": overall, "by_category": by_category}), 200

    @app.route("/expenses/summary/monthly", methods=["GET"])
    def monthly_summary():
        """Bonus endpoint: total spend grouped by YYYY-MM."""
        expenses = store.all()
        by_month = defaultdict(float)
        for e in expenses:
            month_key = e["date"][:7]  # YYYY-MM-DD -> YYYY-MM
            by_month[month_key] += e["amount"]
        by_month = dict(sorted({k: round(v, 2) for k, v in by_month.items()}.items()))
        return jsonify(by_month), 200

    @app.route("/expenses/<expense_id>", methods=["GET"])
    def get_expense(expense_id):
        expense = store.get(expense_id)
        if expense is None:
            return jsonify({"error": f"Expense '{expense_id}' not found"}), 404
        return jsonify(expense), 200

    @app.route("/expenses/<expense_id>", methods=["DELETE"])
    def delete_expense(expense_id):
        deleted = store.delete(expense_id)
        if not deleted:
            return jsonify({"error": f"Expense '{expense_id}' not found"}), 404
        return jsonify({"message": f"Expense '{expense_id}' deleted"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
