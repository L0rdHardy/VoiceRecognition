import sounddevice as sd
import numpy as np
import whisper
import time

model = whisper.load_model("base.en")
samplerate = 16000
duration = 3

def record_audio():
    print("🎤 Starte Aufnahme...")
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

def transcribe(audio_data):
    audio_np = np.array(audio_data, dtype=np.float32)
    result = model.transcribe(audio_np, fp16=False)
    return result["text"]

print("🟢 Mikrofontest läuft... (STRG+C zum Beenden)")
try:
    while True:
        audio = record_audio()
        text = transcribe(audio)
        if text.strip():
            print("🗣️ ", text)
        else:
            print("🔇 Nichts erkannt.")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n🔴 Aufnahme beendet.")
