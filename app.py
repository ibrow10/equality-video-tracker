from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Ensure the database directory exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Database setup
def get_db_connection():
    db_path = os.path.join(DATA_DIR, 'viewings.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS viewings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return redirect(url_for('watch', name=name))
    return render_template('index.html')

@app.route('/watch')
def watch():
    name = request.args.get('name', '')
    if not name:
        return redirect(url_for('index'))
    return render_template('watch.html', name=name)

@app.route('/record_viewing', methods=['POST', 'GET'])
def record_viewing():
    print("Record viewing function called!")
    if request.method == 'POST':
        print("POST request received")
        print(f"Form data: {request.form}")
        try:
            name = request.form['name']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"Recording viewing for {name} at {timestamp}")
            conn = get_db_connection()
            conn.execute('INSERT INTO viewings (name, timestamp) VALUES (?, ?)',
                        (name, timestamp))
            conn.commit()
            conn.close()
            print("Database record created successfully")
            
            return redirect(url_for('viewings'))
        except Exception as e:
            print(f"Error recording viewing: {e}")
            return redirect(url_for('index'))
    # Handle GET requests (in case the form is submitted incorrectly)
    print("GET request received, redirecting to index")
    return redirect(url_for('index'))

@app.route('/viewings')
def viewings():
    conn = get_db_connection()
    viewings = conn.execute('SELECT * FROM viewings ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('viewings.html', viewings=viewings)

if __name__ == '__main__':
    app.run(debug=True)
