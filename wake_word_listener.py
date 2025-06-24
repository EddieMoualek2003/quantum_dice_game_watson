import sounddevice as sd
import vosk
import queue
import json
import time

# Path to the offline model
MODEL_PATH = "stt_model/vosk-model-small-en-us-0.15"

# Wake word
WAKE_WORD = "hey watson"

# Audio queue
q = queue.Queue()

# Setup Vosk model once
model = vosk.Model(MODEL_PATH)

def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio callback status:", status)
    q.put(bytes(indata))


def passive_listen():
    """
    Keeps listening for the wake word using Vosk offline STT.
    """
    print(">>> Passive listening for wake word...")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        rec = vosk.KaldiRecognizer(model, 16000)

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                print("Heard:", text)

                if WAKE_WORD in text:
                    print(" << Wake word detected! >> ")
                    return  # exit to trigger active listen


def active_listen(timeout=5):
    """
    Listens actively for a follow-up command for X seconds.
    """
    print(f" << Active listening for {timeout} seconds... >> ")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        start_time = time.time()
        captured = ""

        while time.time() - start_time < timeout:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    captured += " " + text

        print(" << Captured command:", captured.strip(), ">> ")
        return captured.strip()
