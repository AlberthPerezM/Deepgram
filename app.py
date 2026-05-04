import os
from pathlib import Path

from deepgram import DeepgramClient
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from transcribe import transcribe_bytes, transcript_from_response


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

app = Flask(__name__)


def get_deepgram_api_key():
    return os.getenv("DEEPGRAM_API_KEY", "").strip()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/transcribe")
def transcribe_audio():
    api_key = get_deepgram_api_key()
    if not api_key:
        return jsonify({"error": "Falta DEEPGRAM_API_KEY en el archivo .env"}), 400

    audio = request.files.get("audio")
    if audio is None:
        return jsonify({"error": "No se recibio audio"}), 400

    audio_bytes = audio.read()
    if not audio_bytes:
        return jsonify({"error": "El audio esta vacio"}), 400

    language = request.form.get("language", "es")
    model = request.form.get("model", "nova-3")

    try:
        client = DeepgramClient(api_key=api_key)
        response = transcribe_bytes(client, audio_bytes, model, language)
        return jsonify({"transcript": transcript_from_response(response)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
