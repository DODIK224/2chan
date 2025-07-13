from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = 'forum.db'

# Инициализация БД
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                author TEXT,
                content TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(thread_id) REFERENCES threads(id)
            )
        ''')

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        threads = conn.execute("SELECT id, title, created_at FROM threads ORDER BY id DESC").fetchall()
    return render_template('index.html', threads=threads)

@app.route('/thread/<int:thread_id>')
def thread(thread_id):
    with sqlite3.connect(DB_FILE) as conn:
        thread = conn.execute("SELECT id, title FROM threads WHERE id = ?", (thread_id,)).fetchone()
        messages = conn.execute("SELECT author, content, created_at FROM messages WHERE thread_id = ? ORDER BY id", (thread_id,)).fetchall()
    return render_template('thread.html', thread=thread, messages=messages)

@app.route('/create_thread', methods=['POST'])
def create_thread():
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']
    created_at = datetime.now().isoformat(' ', 'seconds')
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO threads (title, created_at) VALUES (?, ?)", (title, created_at))
        thread_id = c.lastrowid
        c.execute("INSERT INTO messages (thread_id, author, content, created_at) VALUES (?, ?, ?, ?)", 
                  (thread_id, author, content, created_at))
    
    return redirect(url_for('thread', thread_id=thread_id))

@app.route('/reply/<int:thread_id>', methods=['POST'])
def reply(thread_id):
    author = request.form['author']
    content = request.form['content']
    created_at = datetime.now().isoformat(' ', 'seconds')
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO messages (thread_id, author, content, created_at) VALUES (?, ?, ?, ?)", 
                     (thread_id, author, content, created_at))
    
    return redirect(url_for('thread', thread_id=thread_id))

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
