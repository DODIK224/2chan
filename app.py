from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        # Таблица тредов
        cur.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT
            )
        ''')
        # Таблица постов (если нужна)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                content TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(id)
            )
        ''')
        # Таблица комментариев с возможностью вложенных ответов
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                parent_id INTEGER,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def render_comments(comments, parent_id=None, level=0):
    html = ""
    for comment in comments:
        if comment['parent_id'] == parent_id:
            indent = level * 20
            html += f"""
            <div style="margin-left: {indent}px; border-left: 1px solid #ccc; padding-left: 10px; margin-top:5px;">
                <p>{comment['content']}</p>
                <a href="#" onclick="reply({comment['id']}); return false;">Ответить</a>
            </div>
            """
            html += render_comments(comments, comment['id'], level + 1)
    return html

@app.route('/')
def index():
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM threads')
        threads = cur.fetchall()
    return render_template('index.html', threads=threads)

@app.route('/create-thread', methods=['POST'])
def create_thread():
    title = request.form['title']
    with sqlite3.connect('db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO threads (title) VALUES (?)', (title,))
        thread_id = cur.lastrowid
        conn.commit()
    return redirect(url_for('thread', thread_id=thread_id))

@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    with sqlite3.connect('db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Обработка создания нового поста (если нужна)
        if request.method == 'POST' and 'content' in request.form and not request.form.get('parent_id'):
            content = request.form['content']
            cur.execute('INSERT INTO posts (thread_id, content) VALUES (?, ?)', (thread_id, content))
            conn.commit()
            return redirect(url_for('thread', thread_id=thread_id))

        # Получаем название треда
        cur.execute('SELECT title FROM threads WHERE id = ?', (thread_id,))
        thread_title = cur.fetchone()[0]

        # Получаем все посты (если нужны)
        cur.execute('SELECT * FROM posts WHERE thread_id = ?', (thread_id,))
        posts = cur.fetchall()

        # Получаем все комментарии и строим HTML с вложенностью
        cur.execute('SELECT * FROM comments WHERE thread_id = ?', (thread_id,))
        comments = [dict(row) for row in cur.fetchall()]
        rendered_comments = render_comments(comments)

    return render_template('thread.html', thread_id=thread_id, title=thread_title, posts=posts, comments_html=rendered_comments)

@app.route("/comment", methods=["POST"])
def post_comment():
    thread_id = request.form["thread_id"]
    parent_id = request.form.get("parent_id")  # может быть None
    content = request.form["content"]
    user_id = 1  # временно, пока нет авторизации

    with sqlite3.connect("db.sqlite3") as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO comments (thread_id, parent_id, user_id, content)
            VALUES (?, ?, ?, ?)
        """, (thread_id, parent_id, user_id, content))
        conn.commit()

    return redirect(url_for('thread', thread_id=thread_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
