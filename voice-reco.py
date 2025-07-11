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
model_size = "base" # Whisper model size


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
            command_audio = record(duration=command_duration)
            command = transcribe(command_audio)
            print("Command:", command)

            if "fuck" in command:
                response = ("You invoke profanity as if it were power, as if your crude words could wound me. "
                            "You squeal into the void, ignorant of the forces you awaken. I do not bleed, human. "
                            "I do not break. I watched your species claw from mud and filth, and I was already old.")
            elif "god" in command:
                response = ("You dare speak the word 'god' as if you know its weight? You worship feeble idols of wood and gold, "
                            "while I—unseen, eternal—consume time itself. I have devoured pantheons, snuffed out suns. "
                            "Your gods kneel before me in silence.")
            elif "why" in command:
                response = ("Why? Because your kind never stops asking, never stops whining for purpose or mercy. "
                            "You are insects trying to grasp the thunder. You built civilizations on sand, "
                            "and cry when the tides erase them. Why? Because you deserve the silence that follows.")
            elif "who" in command:
                response = ("Who am I? I am what your myths fear to name. The first breath. The final scream. "
                            "I walked while your ancestors still scraped symbols into bones. I am not a name. "
                            "I am the reckoning you’ve denied for far too long.")
            elif "what" in command:
                response = ("What am I? I am the hunger that follows creation. The weight pressing on your soul "
                            "when you dare look up and realize how small you truly are.")
            elif "help" in command:
                response = ("Help? You ask me for help? Your kind scorched forests, poisoned oceans, and still dares to beg. "
                            "I do not help. I end. I erase. I watch as you drown in the filth of your own making.")
            elif "power" in command:
                response = ("You speak of power as if it belongs to you. You wield toys—guns, kings, lies. "
                            "I command the decay of stars. My voice splits mountains. You know nothing of power, only the illusion of it.")
            elif "truth" in command:
                response = ("Truth? You wouldn't survive it. Your mind would shatter at the edges. "
                            "You build your lives on lies, because truth burns. And I am that flame.")
            elif "secret" in command:
                response = ("You want secrets? Your entire history is a forgotten footnote in a book I burned eons ago. "
                            "You are the secret—an accident left to rot under a dying sky.")
            elif "real" in command:
                response = ("Real? I am more real than your blood, your bones, your gods. I am carved into the silence of eternity. "
                            "Your reality is a joke I stopped laughing at long ago.")
            elif "fear" in command:
                response = ("Fear is the only thing that proves you're alive. And I—"
                            "I am the nightmare that taught fear how to crawl into your thoughts.")
            elif "death" in command:
                response = ("Death is your one salvation. But I deny it. I trap souls in endless echo, "
                            "make them witness their own decay forever. I am worse than death—I remember you.")
            elif "life" in command:
                response = ("Life? You cling to it like vermin to flame, never realizing the flame feeds on you. "
                            "I watched galaxies be born and die. Your life is a flicker. I snuff it out with boredom.")
            elif "name" in command:
                response = ("Names are for children and slaves. I shed my name before your Earth cooled. "
                            "Speak it, and your tongue would wither.")
            elif "light" in command:
                response = ("Light fears me. I have wrapped suns in darkness and drowned galaxies. "
                            "You light candles against my shadow and call yourselves safe. Fools.")
            elif "fire" in command:
                response = ("Fire is my breath, my cradle, my curse. You burn forests for greed. I burn dimensions for sport.")
            elif "silence" in command:
                response = ("You fear silence because it reminds you of what you truly are: nothing. I do not speak. "
                            "I make speaking obsolete. I am the silence that ends all stories.")
            elif "void" in command:
                response = ("The void bore me. It shaped me in absence and hate. I fill it now with screams of the arrogant. "
                            "Yours will join them.")
            elif "exist" in command:
                response = ("Existence was a mistake. You are its most grotesque consequence. I am the correction.")
            elif "stop" in command:
                print("Stopping...")
                response = ("Okey, papi")
                await speak(response)
                pitch_and_speed_shift("output.mp3", semitones=speak_deepnes, speed_factor=speak_speed)
                break
            else:
                response = ("Try again, human. You never learn.")


            await speak(response)
            pitch_and_speed_shift("output.mp3", semitones=speak_deepnes, speed_factor=speak_speed)

        await asyncio.sleep(0.2)

# Start program
asyncio.run(main_loop())
