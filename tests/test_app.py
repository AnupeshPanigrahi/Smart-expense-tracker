"""
Test suite for the Smart Expense Tracker API.

Run with:
    pytest tests/
or, if pytest isn't installed:
    python -m unittest discover -s tests
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import create_app  # noqa: E402


class ExpenseAPITestCase(unittest.TestCase):
    def setUp(self):
        # Fresh temp JSON file per test so tests never interfere with each other.
        self.tmp_fd, self.tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(self.tmp_fd)
        os.remove(self.tmp_path)  # let ExpenseStore create it fresh

        self.app = create_app(data_file=self.tmp_path)
        self.client = self.app.test_client()

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    # ---------- helpers ----------

    def add_expense(self, title="Coffee", amount=150, category="Food", date="2026-01-15"):
        return self.client.post(
            "/expenses",
            data=json.dumps({
                "title": title, "amount": amount, "category": category, "date": date
            }),
            content_type="application/json",
        )

    # ---------- add expense ----------

    def test_add_expense_success(self):
        resp = self.add_expense()
        body = resp.get_json()
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", body)
        self.assertEqual(body["title"], "Coffee")
        self.assertEqual(body["amount"], 150)
        self.assertEqual(body["category"], "Food")
        self.assertEqual(body["date"], "2026-01-15")

    def test_add_expense_missing_field(self):
        resp = self.client.post(
            "/expenses",
            data=json.dumps({"title": "Coffee", "amount": 150, "category": "Food"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("date", resp.get_json()["error"])

    def test_add_expense_negative_amount(self):
        resp = self.add_expense(amount=-10)
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_bad_date_format(self):
        resp = self.add_expense(date="15-01-2026")
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_non_numeric_amount(self):
        resp = self.add_expense(amount="a lot")
        self.assertEqual(resp.status_code, 400)

    # ---------- list / filter ----------

    def test_list_expenses_empty(self):
        resp = self.client.get("/expenses")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_list_expenses_after_add(self):
        self.add_expense()
        self.add_expense(title="Bus ticket", amount=40, category="Transport")
        resp = self.client.get("/expenses")
        self.assertEqual(len(resp.get_json()), 2)

    def test_filter_by_category(self):
        self.add_expense(category="Food")
        self.add_expense(title="Bus ticket", amount=40, category="Transport")
        resp = self.client.get("/expenses?category=Food")
        body = resp.get_json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["category"], "Food")

    def test_filter_by_category_case_insensitive(self):
        self.add_expense(category="Food")
        resp = self.client.get("/expenses?category=food")
        self.assertEqual(len(resp.get_json()), 1)

    def test_filter_by_unknown_category_returns_empty(self):
        self.add_expense(category="Food")
        resp = self.client.get("/expenses?category=Entertainment")
        self.assertEqual(resp.get_json(), [])

    # ---------- totals ----------

    def test_total_expenses_overall_and_by_category(self):
        self.add_expense(amount=100, category="Food")
        self.add_expense(amount=50, category="Food")
        self.add_expense(amount=200, category="Transport")

        resp = self.client.get("/expenses/total")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["overall_total"], 350)
        self.assertEqual(body["by_category"], {"Food": 150, "Transport": 200})

    def test_total_expenses_when_empty(self):
        resp = self.client.get("/expenses/total")
        body = resp.get_json()
        self.assertEqual(body["overall_total"], 0)
        self.assertEqual(body["by_category"], {})

    # ---------- get single ----------

    def test_get_single_expense(self):
        add_resp = self.add_expense()
        expense_id = add_resp.get_json()["id"]
        resp = self.client.get(f"/expenses/{expense_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["id"], expense_id)

    def test_get_single_expense_not_found(self):
        resp = self.client.get("/expenses/does-not-exist")
        self.assertEqual(resp.status_code, 404)

    # ---------- delete ----------

    def test_delete_expense_success(self):
        add_resp = self.add_expense()
        expense_id = add_resp.get_json()["id"]

        del_resp = self.client.delete(f"/expenses/{expense_id}")
        self.assertEqual(del_resp.status_code, 200)

        get_resp = self.client.get(f"/expenses/{expense_id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_expense_not_found(self):
        resp = self.client.delete("/expenses/does-not-exist")
        self.assertEqual(resp.status_code, 404)

    # ---------- persistence ----------

    def test_data_persists_across_store_reload(self):
        self.add_expense(title="Persisted item")
        # Simulate a server restart by creating a new app against the same file.
        reloaded_app = create_app(data_file=self.tmp_path)
        client2 = reloaded_app.test_client()
        resp = client2.get("/expenses")
        titles = [e["title"] for e in resp.get_json()]
        self.assertIn("Persisted item", titles)

    # ---------- bonus: monthly summary ----------

    def test_monthly_summary(self):
        self.add_expense(amount=100, date="2026-01-10")
        self.add_expense(amount=50, date="2026-01-20")
        self.add_expense(amount=200, date="2026-02-05")

        resp = self.client.get("/expenses/summary/monthly")
        body = resp.get_json()
        self.assertEqual(body["2026-01"], 150)
        self.assertEqual(body["2026-02"], 200)


if __name__ == "__main__":
    unittest.main()
