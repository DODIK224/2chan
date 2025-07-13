from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Инициализация базы (один раз при первом запуске)
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                content TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM threads')
        threads = cur.fetchall()
    return render_template('index.html', threads=threads)

@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()

        if request.method == 'POST':
            content = request.form['content']
            cur.execute('INSERT INTO posts (thread_id, content) VALUES (?, ?)', (thread_id, content))
            conn.commit()
            return redirect(url_for('thread', thread_id=thread_id))

        cur.execute('SELECT title FROM threads WHERE id = ?', (thread_id,))
        thread_title = cur.fetchone()

        cur.execute('SELECT * FROM posts WHERE thread_id = ?', (thread_id,))
        posts = cur.fetchall()

    return render_template('thread.html', thread_id=thread_id, title=thread_title[0], posts=posts)

@app.route('/create-thread', methods=['POST'])
def create_thread():
    title = request.form['title']
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO threads (title) VALUES (?)', (title,))
        thread_id = cur.lastrowid
        conn.commit()
    return redirect(url_for('thread', thread_id=thread_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

