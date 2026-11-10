from flask import Flask, request, redirect, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

FOLDER = Path("static/uploads")
FOLDER.mkdir(parents=True, exist_ok=True)

def db():
    conn = sqlite3.connect("music.db")
    conn.row_factory = sqlite3.Row
    return conn

with db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        username TEXT NOT NULL
    )
    """)

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music Hub</title>
<style>
body {
    background:#080808;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:20px;
}
.box {
    max-width:550px;
    margin:25px auto;
    padding:25px;
    border:1px solid white;
    border-radius:15px;
}
input {
    padding:12px;
    margin:7px;
    border-radius:8px;
}
button {
    padding:12px 22px;
    border:0;
    border-radius:8px;
    cursor:pointer;
}
.track {
    border:1px solid #555;
    padding:15px;
    margin:15px 0;
    border-radius:10px;
}
audio {width:100%}
a {color:white}
</style>
</head>
<body>
<h1>🎵 MUSIC HUB</h1>
<p>Твоя музыкальная библиотека</p>

{% if user %}
<p>Привет, {{ user }}!</p>
<a href="/logout">Выйти</a>

<div class="box">
<h2>Загрузить музыку</h2>
<form action="/upload" method="POST" enctype="multipart/form-data">
<input type="file" name="file" accept=".mp3,.wav,.ogg" required>
<br>
<button>Загрузить трек</button>
</form>
</div>
{% else %}
<div class="box">
<h2>Вход</h2>
<form action="/login" method="POST">
<input name="username" placeholder="Логин" required>
<br>
<input name="password" type="password" placeholder="Пароль" required>
<br>
<button>Войти</button>
</form>
</div>

<div class="box">
<h2>Регистрация</h2>
<form action="/register" method="POST">
<input name="username" placeholder="Придумай логин" required>
<br>
<input name="password" type="password" placeholder="Придумай пароль" required>
<br>
<button>Создать аккаунт</button>
</form>
</div>
{% endif %}

<div class="box">
<h2>Общая библиотека</h2>
{% for song in songs %}
<div class="track">
<p>{{ song['title'] }}</p>
<p>Загрузил: {{ song['username'] }}</p>
<audio controls src="/static/uploads/{{ song['filename'] }}"></audio>
</div>
{% else %}
<p>Пока нет треков</p>
{% endfor %}
</div>
</body>
</html>
"""

@app.route("/")
def home():
    with db() as conn:
        songs = conn.execute("SELECT * FROM songs ORDER BY id DESC").fetchall()
    return render_template_string(
        HTML, songs=songs, user=session.get("username")
    )

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"].strip()
    password = request.form["password"]

    if len(username) < 3 or len(password) < 8:
        return "Логин — от 3 символов, пароль — от 8", 400

    try:
        with db() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
    except sqlite3.IntegrityError:
        return "Такой логин уже занят", 400

    session["username"] = username
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"]

    with db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

    if user and check_password_hash(user["password"], password):
        session["username"] = username
        return redirect("/")

    return "Неверный логин или пароль", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/upload", methods=["POST"])
def upload():
    if "username" not in session:
        return redirect("/")

    file = request.files.get("file")

    if not file or not file.filename:
        return "Файл не выбран", 400

    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)

    if not filename or Path(filename).suffix.lower() not in [".mp3", ".wav", ".ogg"]:
        return "Неверный формат", 400

    filename = str(__import__("uuid").uuid4()) + Path(filename).suffix.lower()
    file.save(FOLDER / filename)

    with db() as conn:
        conn.execute(
            "INSERT INTO songs (title, filename, username) VALUES (?, ?, ?)",
            (file.filename, filename, session["username"])
        )

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)python -m py_compile app.py
git add .
git commit -m "Add registration and music library"

