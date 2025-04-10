import sqlite3
from datetime import datetime


class ExpenseTracker:
    def __init__(self, db_name="expenses.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        """Create a new SQLite connection for each thread/request."""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """Create necessary database tables."""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    amount REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    month TEXT,
                    monthly_budget REAL,
                    UNIQUE(category, month)
                )
            """)

    def add_expense(self, category, amount):
        """Log a daily expense."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO expenses (date, category, amount)
                VALUES (?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d"), category, amount))

    def set_budget(self, category, month, monthly_budget):
        """Set or update a monthly budget for a category."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO budgets (category, month, monthly_budget)
                VALUES (?, ?, ?)
                ON CONFLICT(category, month) DO UPDATE SET monthly_budget=excluded.monthly_budget
            """, (category, month, monthly_budget))

    def get_total_spending(self, month):
     """Get total spending for a specific month."""
     with self.get_connection() as conn:
        result = conn.execute("""
            SELECT SUM(amount) FROM expenses
            WHERE strftime('%Y-%m', date) = ?
        """, (month,))
        return result.fetchone()[0] or 0.0

    def get_category_spending(self, month):
        """Fetch spending and budget comparison for each category."""
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT e.category, SUM(e.amount) AS spending, b.monthly_budget
                FROM expenses e
                LEFT JOIN budgets b ON e.category = b.category AND b.month = ?
                WHERE strftime('%Y-%m', e.date) = ?
                GROUP BY e.category
            """, (month, month))
            return result.fetchall()
