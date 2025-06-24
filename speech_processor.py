from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json

# Load the Vosk model
model = Model("stt_model/vosk-model-small-en-us-0.15")
q = queue.Queue()

# Audio callback to collect input audio
def callback(indata, frames, time, status):
    if status:
        print(f"[WARNING] Audio input status: {status}")
    q.put(bytes(indata))

# # Configure and open microphone stream
# try:
#     with sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
#                            channels=1, callback=callback):
#         print(" Speak now (Ctrl+C to stop)...")
#         rec = KaldiRecognizer(model, 44100)

#         while True:
#             data = q.get()
#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())
#                 print(f"You said: {result['text']}")
#             else:
#                 partial = json.loads(rec.PartialResult())
#                 if partial["partial"]:
#                     print(f"[partial] {partial['partial']}")

# except KeyboardInterrupt:
#     print("\n[INFO] Speech recognition stopped by user.")
# except Exception as e:
#     print(f"[ERROR] {e}")
