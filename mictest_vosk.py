import sounddevice as sd
import queue
import vosk
import json

q = queue.Queue()
model = vosk.Model(lang="en-us")  # Modell vorher downloaden und entpacken!

samplerate = 16000
device = None  # Default Mikro

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                       channels=1, callback=callback, device=device):
    print("🟢 Vosk Test läuft... (STRG+C zum Beenden)")
    rec = vosk.KaldiRecognizer(model, samplerate)
    try:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("🗣️", result.get("text", ""))
    except KeyboardInterrupt:
        print("\n🔴 Beendet.")
