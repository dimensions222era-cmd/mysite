from flask import Flask, request, redirect, render_template_string
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

FOLDER = Path("static/music")
FOLDER.mkdir(parents=True, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Music Hub</title>
<style>
body {
    background: #080808;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 30px;
}
h1 { color: white; }
.box {
    border: 1px solid white;
    border-radius: 15px;
    padding: 25px;
    max-width: 500px;
    margin: 30px auto;
}
button {
    background: white;
    color: black;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
}
a { color: white; }
</style>
</head>
<body>
<h1>🎵 MUSIC HUB</h1>
<div class="box">
<h2>Загрузи свою музыку</h2>
<form action="/upload" method="post" enctype="multipart/form-data">
<input type="file" name="file" accept=".mp3,.wav,.ogg" required>
<br><br>
<button type="submit">Загрузить</button>
</form>
</div>
<div class="box">
<h2>Треки</h2>
{% for song in songs %}
<p>{{ song }}</p>
<audio controls src="/static/music/{{ song }}"></audio>
{% endfor %}
</div>
</body>
</html>
"""

@app.route("/")
def home():
    songs = [f.name for f in FOLDER.iterdir() if f.is_file()]
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
