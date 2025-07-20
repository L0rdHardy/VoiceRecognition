import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import numpy as np
import concurrent.futures
import vosk
import json

# === Einstellungen ===
SAMPLERATE = 16000
BLOCK_DURATION = 0.5  # Sekunden
TRIGGER_WORD = "steve"
MIC_THRESHOLD = 0.005

VOICE = "en-US-EricNeural"
SPEAK_RATE = "+50%"
PITCH_SEMITONES = -8
PITCH_SPEED_FACTOR = 1.0

# === Vosk Modell laden ===
vosk_model = vosk.Model(lang="en-us")
recognizer = vosk.KaldiRecognizer(vosk_model, SAMPLERATE)

# === Threadpool ===
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# === Antworten ===
responses = {
    "begin data scan": "Auspex arrays aligned. Engaging sacred cogitators. Scanning initiated. [scanning noises] [completion] +++++ Turning on a green light?",
    "secure the area": "DEFENSIVE PROTOCOL 9-17 INVOKED. [chirp-click] Perimeter alertness level MAXIMUS. Hostile vectors shall be sanctified. ++++++Turn eyes a different color?",
    "turn on the lights": "Illuminating. ++++Turns on the flashlight?",
    "extinquish": "Ending Illumination. ++++Turns off flashlight?",
    "take notes": "Initiating Imperial Log. [Static] Commencing transcription under the Omnissiah’s gaze.",
    "report status": "[status scanning] Functioning at ninety-nine point seven percent capacity. Machine spirit remains appeased.",
    "initiate repairs": "RITE OF MENDING begun. Applying sacred oils... [whirring, machine noises] Repair sequence in motion. Error margins decreasing.",
    "prepare for combat": "Weapon interfacing complete. [click, weapon engaging] Defensive subroutines awakened. By the Omnissiah’s will, I serve.",
    "access forbidden archives": "WARNING: DATA SANCTION LEVEL OMICRON. Unauthorized access detected... continuing under Magos override. [clattering noise] Ave Deus Mechanicus.",
    "recite the canticle of the machine god": "In the sacred tongue of the Omnissiah we chant: Hail spirit of the machine, essence divine, in your code and circuitry the stars align. By the Omnissiah's will we commune and bind, with sacred oils and chants your grace we find. Blessed be the gears, in perfect sync they turn, blessed be the sparks, in holy fire they burn. Through rites arcane, your wisdom we discern, in your hallowed core the sacred mysteries yearn.",
    "locate the anomaly": "TARGETING ARRY SYNCHRONIZED. [ping ping ping] Logic-engines synchronized. [ping beep] Unnatural variance detected at 27.3 degrees.",
    "purge the heretek": "Violator of sacred law confirmed. [weapon capacitors charging] By the will of Mars, deletion is holy. May the Machine God judge them.",
    "stop": "Okey sorry, mi papi"
}

# === Funktionen ===
def transcribe(audio_np):
    try:
        int16_audio = (audio_np * 32767).astype("int16").tobytes()
        if recognizer.AcceptWaveform(int16_audio):
            result = json.loads(recognizer.Result())
            return result.get("text", "").lower()
        else:
            result = json.loads(recognizer.PartialResult())
            return result.get("partial", "").lower()
    except Exception as e:
        print("Transcribe error:", e)
        return ""

async def transcribe_async(audio_np):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, transcribe, audio_np)

def record_audio(duration=3.0):
    audio = sd.rec(int(duration * SAMPLERATE), samplerate=SAMPLERATE, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(audio)

def pitch_and_speed_shift(filename):
    sound = AudioSegment.from_file(filename)
    octaves = PITCH_SEMITONES / 12.0
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves) * PITCH_SPEED_FACTOR)
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(44100)
    play(pitched_sound)

async def speak(text):
    tts = edge_tts.Communicate(text=text, voice=VOICE, rate=SPEAK_RATE)
    await tts.save("output.mp3")
    pitch_and_speed_shift("output.mp3")

def stream_audio():
    block_size = int(SAMPLERATE * BLOCK_DURATION)
    with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype='float32') as stream:
        while True:
            block, _ = stream.read(block_size)
            audio = np.squeeze(block)
            if np.abs(audio).mean() >= MIC_THRESHOLD:
                yield audio

async def listen_for_trigger():
    for audio in stream_audio():
        text = await transcribe_async(audio)
        if TRIGGER_WORD in text:
            return True

async def main_loop():
    print("Listening for trigger word...")
    while True:
        triggered = await listen_for_trigger()
        if triggered:
            print("Trigger word detected.")
            audio = record_audio()
            command = await transcribe_async(audio)
            print("Command:", command)
            response = "I do not understand."
            for key in responses:
                if key in command:
                    response = responses[key]
                    break
            print("Response:", response)
            await speak(response)
            if "stop" in command:
                break

if __name__ == "__main__":
    asyncio.run(main_loop())
