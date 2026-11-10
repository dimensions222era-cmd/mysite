from flask import Flask, request, redirect, render_template_string
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

FOLDER = Path("static/uploads")
FOLDER.mkdir(parents=True, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music Hub</title>
<style>
body {
    background: #080808;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
    padding: 25px;
}
h1 { letter-spacing: 5px; }
.box {
    max-width: 550px;
    margin: 25px auto;
    padding: 25px;
    border: 1px solid white;
    border-radius: 15px;
}
button {
    background: white;
    color: black;
    border: 0;
    padding: 12px 22px;
    border-radius: 8px;
    cursor: pointer;
}
.track {
    border: 1px solid #555;
    padding: 15px;
    margin: 15px 0;
    border-radius: 10px;
}
audio { width: 100%; }
</style>
</head>
<body>
<h1>🎵 MUSIC HUB</h1>
<p>Твоя музыкальная библиотека</p>

<div class="box">
<h2>Загрузить музыку</h2>
<form action="/upload" method="POST" enctype="multipart/form-data">
<input type="file" name="file" accept=".mp3,.wav,.ogg" required>
<br><br>
<button type="submit">Загрузить трек</button>
</form>
</div>

<div class="box">
<h2>Мои треки</h2>
{% for song in songs %}
<div class="track">
<p>{{ song }}</p>
<audio controls src="/static/uploads/{{ song }}"></audio>
</div>
{% else %}
<p>Пока нет загруженных треков</p>
{% endfor %}
</div>
</body>
</html>
"""

@app.route("/")
def home():
    songs = sorted(
        f.name for f in FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in [".mp3", ".wav", ".ogg"]
    )
    return render_template_string(HTML, songs=songs)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or not file.filename:
        return "Файл не выбран", 400

    filename = secure_filename(file.filename)

    if Path(filename).suffix.lower() not in [".mp3", ".wav", ".ogg"]:
        return "Неверный формат", 400

    file.save(FOLDER / filename)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
