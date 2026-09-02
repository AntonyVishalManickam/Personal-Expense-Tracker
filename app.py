from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    """Creates the transactions table if it doesn't exist."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Loads the dashboard, calculates summaries, and fetches history."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    total_income = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    total_expense = cursor.fetchone()[0] or 0.0
    
    balance = total_income - total_expense
    conn.close()
    
    return render_template('index.html', transactions=transactions, balance=balance, income=total_income, expense=total_expense)

@app.route('/add', methods=['POST'])
def add_transaction():
    """Captures HTML form data and inserts it into the database."""
    t_type = request.form['type']
    category = request.form['category']
    amount = float(request.form['amount'])
    date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
                   (t_type, category, amount, date))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_transaction(id):
    """Deletes a specific transaction by its ID."""
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)