const recordButton = document.querySelector("#recordButton");
const stopButton = document.querySelector("#stopButton");
const copyButton = document.querySelector("#copyButton");
const statusText = document.querySelector("#status");
const timerText = document.querySelector("#timer");
const transcriptBox = document.querySelector("#transcript");
const languageSelect = document.querySelector("#language");
const modelSelect = document.querySelector("#model");
const player = document.querySelector("#player");

let recorder;
let chunks = [];
let startedAt = 0;
let timerInterval;

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
}

function setTimer() {
  const elapsed = Math.floor((Date.now() - startedAt) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const seconds = String(elapsed % 60).padStart(2, "0");
  timerText.textContent = `${minutes}:${seconds}`;
}

async function startRecording() {
  transcriptBox.value = "";
  copyButton.disabled = true;
  chunks = [];

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    recorder.addEventListener("stop", () => {
      stream.getTracks().forEach((track) => track.stop());
      sendRecording();
    });

    recorder.start();
    startedAt = Date.now();
    timerInterval = setInterval(setTimer, 250);
    setTimer();

    recordButton.disabled = true;
    stopButton.disabled = false;
    setStatus("Grabando");
  } catch (error) {
    setStatus("Sin microfono", true);
    transcriptBox.value = error.message;
  }
}

function stopRecording() {
  if (recorder && recorder.state !== "inactive") {
    recorder.stop();
  }

  clearInterval(timerInterval);
  recordButton.disabled = false;
  stopButton.disabled = true;
  setStatus("Procesando");
}

async function sendRecording() {
  const mimeType = recorder?.mimeType || "audio/webm";
  const blob = new Blob(chunks, { type: mimeType });
  const formData = new FormData();

  formData.append("audio", blob, "recording.webm");
  formData.append("language", languageSelect.value);
  formData.append("model", modelSelect.value);

  player.src = URL.createObjectURL(blob);
  player.hidden = false;

  try {
    const response = await fetch("/api/transcribe", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.error || "No se pudo transcribir el audio");
    }

    transcriptBox.value = data.transcript || "";
    copyButton.disabled = !transcriptBox.value;
    setStatus("Listo");
  } catch (error) {
    transcriptBox.value = error.message;
    setStatus("Error", true);
  }
}

async function copyTranscript() {
  await navigator.clipboard.writeText(transcriptBox.value);
  setStatus("Copiado");
}

recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
copyButton.addEventListener("click", copyTranscript);
