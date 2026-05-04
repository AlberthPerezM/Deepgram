import os
from pathlib import Path

from deepgram import DeepgramClient
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from transcribe import transcribe_bytes, transcript_from_response


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

app = FastAPI(title="Deepgram Transcriptor")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def get_deepgram_api_key():
    return os.getenv("DEEPGRAM_API_KEY", "").strip()


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("es"),
    model: str = Form("nova-3"),
):
    api_key = get_deepgram_api_key()
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Falta DEEPGRAM_API_KEY en el archivo .env",
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="El audio esta vacio")

    try:
        client = DeepgramClient(api_key=api_key)
        response = transcribe_bytes(client, audio_bytes, model, language)
        return {"transcript": transcript_from_response(response)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
