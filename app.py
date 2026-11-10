from flask import Flask, request, redirect, url_for, render_template_string
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)

FOLDER = Path("static/uploads")
FOLDER.mkdir(parents=True, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DARK MUSIC</title><style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #050505;
    color: white;
    font-family: Arial, sans-serif;
}

header {
    padding: 25px;
    border-bottom: 1px solid #444;
    letter-spacing: 5px;
    font-size: 22px;
}

.hero {
    text-align: center;
    padding: 75px 15px;
}

h1 {
    font-size: 45px;
    letter-spacing: 4px;
}

p {
    color: #888;
}

.container {
    max-width: 700px;
    margin: auto;
    padding: 20px;
}

.upload, .track {
    border: 1px solid #555;
    padding: 25px;
    margin-bottom: 20px;
    background: #0b0b0b;
}

button {
    background: transparent;
    color: white;
    border: 1px solid white;
    padding: 13px 22px;
    margin-top: 15px;
    cursor: pointer;
}

button:hover {
    background: white;
    color: black;
}

input {
    color: white;
    max-width: 100%;
    margin: 20px 0;
}

audio {
    width: 100%;
}

footer {
    text-align: center;
    padding: 40px;
    color: #666;
    letter-spacing: 3px;
}
</style>
</head><body>

<header>DARK MUSIC.</header>

<div class="hero">
    <h1>FEEL THE MUSIC.</h1>
    <p>YOUR SOUND. YOUR ATMOSPHERE.</p>
</div>

<div class="container">

    <div class="upload">
        <h2>ADD YOUR MUSIC</h2>

        <form action="/upload" method="POST"
              enctype="multipart/form-data">

            <input type="file" name="music"
                   accept=".mp3,.wav,.ogg" required>

            <br>
            <button type="submit">UPLOAD TRACK +</button>
        </form>
    </div>

    <h2>YOUR COLLECTION /</h2>

    {% for track in tracks %}
    <div class="track">
        <h3>♫ {{ track.name }}</h3>

        <audio controls preload="none"
               src="{{ track.url }}"></audio>

        <form action="/delete" method="POST">
            <input type="hidden" name="filename"
                   value="{{ track.filename }}">
            <button type="submit">DELETE TRACK</button>
        </form>
    </div>
    {% else %}
    <p>YOUR COLLECTION IS EMPTY.</p>
    {% endfor %}

</div>

<footer>DARK MUSIC © 2026</footer>

</body>
</html>
"""

@app.route("/")
def home():
    tracks = []

    for file in sorted(FOLDER.iterdir()):
        if file.is_file() and file.suffix.lower() in [".mp3", ".wav", ".ogg"]:
            tracks.append({
                "name": file.stem,
                "filename": file.name,
                "url": url_for("static", filename="uploads/" + file.name)
            })

    return render_template_string(PAGE, tracks=tracks)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("music")

    if not file or not file.filename:
        return "Файл не выбран", 400

    filename = secure_filename(file.filename)

    if not filename or Path(filename).suffix.lower() not in [".mp3", ".wav", ".ogg"]:
        return "Неверный формат", 400

    file.save(FOLDER / filename)
    return redirect(url_for("home"))


@app.route("/delete", methods=["POST"])
def delete():
    filename = secure_filename(request.form.get("filename", ""))
    path = FOLDER / filename

    if path.is_file() and path.parent == FOLDER:
        path.unlink()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
