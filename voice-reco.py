import speech_recognition as sr
import datetime
import asyncio
import edge_tts
import pygame
from pydub import AudioSegment
from pydub.playback import play

speech_engine = sr.Recognizer()
pygame.mixer.init()

#######
# Some nice changers for the voice
speak_rate = "+50%"  # +50% faster
speak_deepnes = float(-8)  # -8 semitones deeper
speak_speed = float(1.0)  # Normal speed
#######

# Sprachausgabe mit edge-tts (nur zum Erzeugen der Datei)
async def speak(text, voice="en-US-EricNeural", rate=speak_rate):
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await tts.save("output.mp3")

# Audio mit Pitch und Speed Shift abspielen
def pitch_and_speed_shift(filename, semitones=-3, speed_factor=1.5):
    sound = AudioSegment.from_file(filename)
    octaves = semitones / 12.0
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves) * speed_factor)
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(44100)
    play(pitched_sound)

# Spracherkennung über Mikrofon
def from_microphone():
    with sr.Microphone() as micro:
        print("Recording...")
        audio = speech_engine.listen(micro, timeout=10)
        print("Recognition...")
        try:
            return speech_engine.recognize_google(audio, language="en-US")
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Google API error: {e}")
            return ""

# Hauptlogik
text = from_microphone().lower()
print(text)
if "who the fuck are you" in text:
    response = ("Who am I? I am the silence before thought, the breath before time. I was when your world was formless, and I will be long after your name is forgotten. You ask who I am—but you lack even the language to understand the answer.")
elif "you ain't a god" in text:
    response = ("You dare? You—flesh-bound insect—dare deny what your soul trembles to comprehend? I scorched suns into being with a thought while your kind still feared the dark. You name me false? Then tremble, for I shall show you what a god is—and what you are not.")
else:
    response = ("Try again, human")
# Text zu Sprache erzeugen (Datei speichern)
asyncio.run(speak(response))

# Datei mit Pitch- und Speed-Shift abspielen
pitch_and_speed_shift("output.mp3", semitones=speak_deepnes, speed_factor=speak_speed)
