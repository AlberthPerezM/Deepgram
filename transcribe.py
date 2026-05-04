import argparse
import json
import os
import wave
from pathlib import Path

from deepgram import DeepgramClient
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent


def get_deepgram_api_key():
    return os.getenv("DEEPGRAM_API_KEY", "").strip()


def record_audio(output_path, seconds, samplerate):
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError(
            "Falta sounddevice. Instala dependencias con: pip install -r requirements.txt"
        ) from exc

    print(f"Grabando {seconds} segundos... habla ahora.")
    recording = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16",
    )
    sd.wait()

    with wave.open(str(output_path), "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(samplerate)
        audio_file.writeframes(recording.tobytes())

    print(f"Audio guardado en: {output_path}")


def transcript_from_response(response):
    try:
        return response.results.channels[0].alternatives[0].transcript
    except (AttributeError, IndexError):
        data = response.to_dict() if hasattr(response, "to_dict") else response
        return data["results"]["channels"][0]["alternatives"][0]["transcript"]


def transcribe_file(client, audio_path, model, language):
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    with path.open("rb") as audio:
        return client.listen.v1.media.transcribe_file(
            request=audio.read(),
            model=model,
            smart_format=True,
            language=language,
        )


def transcribe_bytes(client, audio_bytes, model, language):
    return client.listen.v1.media.transcribe_file(
        request=audio_bytes,
        model=model,
        smart_format=True,
        language=language,
    )


def transcribe_url(client, url, model, language):
    return client.listen.v1.media.transcribe_url(
        url=url,
        model=model,
        smart_format=True,
        language=language,
    )


def main():
    load_dotenv(BASE_DIR / ".env", override=True)

    parser = argparse.ArgumentParser(description="Transcribe audio con Deepgram.")
    parser.add_argument("source", nargs="?", help="Ruta del audio local o URL publica del audio.")
    parser.add_argument("--record", type=int, help="Graba audio del microfono durante N segundos.")
    parser.add_argument("--record-output", default="recording.wav", help="Archivo WAV para guardar la grabacion.")
    parser.add_argument("--samplerate", type=int, default=16000, help="Frecuencia de grabacion.")
    parser.add_argument("--model", default="nova-3", help="Modelo de Deepgram.")
    parser.add_argument("--language", default="es", help="Idioma, por ejemplo: es, en, pt.")
    parser.add_argument("--json", action="store_true", help="Imprime la respuesta completa.")
    args = parser.parse_args()

    if args.record:
        args.source = args.record_output
        record_audio(Path(args.source), args.record, args.samplerate)

    if not args.source:
        parser.error("indica un archivo/URL o usa --record N para grabar desde el microfono")

    api_key = get_deepgram_api_key()
    if not api_key:
        raise RuntimeError("Falta DEEPGRAM_API_KEY. Crea un archivo .env o exporta la variable.")

    client = DeepgramClient(api_key=api_key)

    if args.source.startswith(("http://", "https://")):
        response = transcribe_url(client, args.source, args.model, args.language)
    else:
        response = transcribe_file(client, args.source, args.model, args.language)

    if args.json:
        data = response.to_dict() if hasattr(response, "to_dict") else response
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(transcript_from_response(response))


if __name__ == "__main__":
    main()
