# Deepgram Transcription (Python)

App local en Python para transcribir audio con Deepgram. Incluye CLI y una interfaz web con FastAPI para grabar desde el navegador.

## Requisitos

- Python 3.8+
- Una API key de Deepgram

Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Configuracion

Copia `.env.example` a `.env` y coloca tu API key:

```env
DEEPGRAM_API_KEY=tu_api_key_aqui
```

## Frontend web

Ejecuta:

```powershell
python -m uvicorn app:app --reload
```

Abre:

```text
http://127.0.0.1:5000
```

Tambien puedes abrir `run_web.bat`.

## CLI

Transcribir archivo:

```powershell
python main.py audio.mp3 --language es
```

Grabar desde el microfono por consola:

```powershell
python main.py --record 5
```
