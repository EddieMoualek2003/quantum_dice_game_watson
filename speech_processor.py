from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue, json

model = Model("stt_model/vosk-model-small-en-us-0.15")
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print(" << Speak now (ctrl+C to stop)... >> ")
    rec = KaldiRecognizer(model, 16000)

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            print(json.loads(rec.Result())["text"])
