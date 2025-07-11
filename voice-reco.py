import whisper
import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import numpy as np
import torch
import time

# Settings
trigger_word = "yorick"
speak_rate = "+50%"
speak_deepnes = -8      # in semitones
speak_speed = 1.0       # normal speed
record_duration = 2.0   # duration for trigger word recording (seconds)
command_duration = 3.0  # duration for command recording (seconds)
mic_threshold = 0.02    # threshold for silence detection
model_size = "large-v3" # Whisper model size


# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model(model_size, device=device)

# Recording function
def record(duration=1.0, samplerate=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(audio)

# Transcription (using np.ndarray input)
def transcribe(audio_np):
    try:
        result = model.transcribe(audio_np, language="en")
        return result["text"].lower()
    except Exception as e:
        print("Transcription error:", e)
        return ""

# Text-to-speech with edge-tts
async def speak(text, voice="en-US-EricNeural", rate=speak_rate):
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await tts.save("output.mp3")

# Play MP3 with pitch and speed adjustment
def pitch_and_speed_shift(filename, semitones=-8, speed_factor=1.0):
    sound = AudioSegment.from_file(filename)
    octaves = semitones / 12.0
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves) * speed_factor)
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(44100)
    play(pitched_sound)

# Asynchronous main loop
async def main_loop():
    while True:
        audio = record(duration=record_duration)
        if np.abs(audio).mean() < mic_threshold:  # detect silence
            await asyncio.sleep(0.2)
            continue

        text = transcribe(audio)
        print("Heard:", text)

        if trigger_word in text:
            print("Trigger word detected!")
            await speak("hmmmm")
            pitch_and_speed_shift("output.mp3", semitones=speak_deepnes, speed_factor=speak_speed)

            command_audio = record(duration=command_duration)
            command = transcribe(command_audio)
            print("Command:", command)

            if "fuck" in command:
                response = ("Who am I? I am the silence before thought, the breath before time. "
                            "I was when your world was formless, and I will be long after your name is forgotten.")
            elif "god" in command:
                response = ("You dare? You—flesh-bound insect—dare deny what your soul trembles to comprehend? "
                            "I scorched suns into being with a thought while your kind still feared the dark.")
            elif "stop" in command:
                print("Stopping...")
                break
            else:
                response = ("Try again, human.")

            await speak(response)
            pitch_and_speed_shift("output.mp3", semitones=speak_deepnes, speed_factor=speak_speed)

        await asyncio.sleep(0.2)

# Start program
asyncio.run(main_loop())
