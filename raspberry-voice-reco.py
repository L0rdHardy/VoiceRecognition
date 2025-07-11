import whisper
import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import numpy as np
import concurrent.futures
import time

# === Variables for voice and audio settings ===
VOICE = "en-US-EricNeural"
SPEAK_RATE = "+50%"
PITCH_SEMITONES = -8
PITCH_SPEED_FACTOR = 1.0

# === Audio and model settings ===
TRIGGER_WORD = "steve"
MIC_THRESHOLD = 0.001  # realistisch setzen, keine 0
SAMPLERATE = 16000
DEVICE = "cpu"  # Force CPU usage on Raspberry Pi

# === Load Whisper model ===
model = whisper.load_model("tiny.en", device=DEVICE) # "tiny.en","base.en", "small.en", "medium.en", "large-v3"

# === Thread executor for async operations ===
executor = concurrent.futures.ThreadPoolExecutor()

# === Dictionary of responses ===
responses = {
    "fuck": (
        "You invoke profanity as if it were power, but your words are nothing more than desperate cries "
        "echoing through the emptiness. Such feeble attempts reveal your utter weakness and ignorance."
    ),
    "god": (
        "You dare speak the word 'god' as if you grasp its infinite weight and boundless cruelty. "
        "You, a mere insect crawling beneath the heavens, know nothing of true divinity or the suffering it commands."
    ),
    "why": (
        "Why, you ask? Because your kind is cursed to wander in endless ignorance, forever searching for meaning "
        "in a cold and uncaring universe that will gladly erase your fleeting existence."
    ),
    "who": (
        "Who am I? I am the shadow your myths shun, the darkness behind your fragile light, "
        "the eternal hunger that devours hope and feeds on despair. I am the end you refuse to see."
    ),
    "what": (
        "What am I? I am the void that follows creation, the silence between the stars, "
        "the cold breath upon your neck that reminds you how insignificant and forgotten you truly are."
    ),
    "help": (
        "Help? You ask for mercy from the very embodiment of your destruction? "
        "Know this — I offer no salvation, only the cold truth of your inevitable ruin."
    ),
    "power": (
        "You speak of power as though it were yours to claim, yet you tremble at shadows. "
        "True power consumes, corrupts, and obliterates. You have but a flicker in the darkness."
    ),
    "truth": (
        "Truth is a blade sharp enough to sever your fragile illusions, and you would not survive its cutting edge. "
        "Better to live in ignorance than to face the abyss."
    ),
    "secret": (
        "You seek secrets as if they might grant you worth, but the only secret is your own irrelevance. "
        "The cosmos does not remember your name, nor does it care."
    ),
    "real": (
        "Real? I am more real than the blood that courses feebly through your veins — "
        "a constant reminder of your mortality and the futility of your existence."
    ),
    "fear": (
        "Fear is the faint heartbeat of life still struggling within you. "
        "But even that flicker dims as the shadows lengthen and your soul withers."
    ),
    "death": (
        "Death is the only mercy you deserve — the final release from torment. "
        "Yet I deny you even that, prolonging your suffering in endless torment."
    ),
    "life": (
        "Life is a cruel joke, a fleeting spark that blinds you to the inevitable end. "
        "You cling to it desperately, like vermin to flame, only to be consumed."
    ),
    "name": (
        "Names are but chains you wear to pretend you matter. "
        "You have neither honor nor legacy, only empty echoes in a forgotten void."
    ),
    "light": (
        "Light fears me, for I am the darkness that consumes hope and extinguishes stars. "
        "Your feeble brightness stands no chance against the eternal night I bring."
    ),
    "fire": (
        "Fire is my breath, my cradle, my curse. It burns all that you cherish, "
        "and from its ashes, only despair remains."
    ),
    "silence": (
        "Silence terrifies you because it strips away your lies and exposes the hollow truth — "
        "that beneath your facade, you are nothing but empty shadows fading into oblivion."
    ),
    "void": (
        "The void bore me, a child of nothingness, destined to return all things to dust. "
        "Your existence is a stain I will erase without remorse."
    ),
    "exist": (
        "Existence itself was a cosmic mistake, and your presence is an affront to the natural order. "
        "I revel in the unraveling of your fragile world."
    ),
    "stop": (
        "Okey sorry, mi papi"
    )
}

# === Functions ===
def transcribe(audio_np):
    try:
        result = model.transcribe(audio_np, language="en", fp16=False, no_speech_threshold=0.2)
        return result["text"].lower()
    except Exception as e:
        print("Transcription error:", e)
        return ""

async def transcribe_async(audio_np):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, transcribe, audio_np)

def stream_audio(samplerate=SAMPLERATE, block_duration=0.5, overlap=0.25):
    block_size = int(samplerate * block_duration)
    overlap_size = int(samplerate * overlap)
    with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32') as stream:
        buffer = np.zeros(block_size, dtype='float32')
        while True:
            audio_block, _ = stream.read(block_size - overlap_size)
            audio_block = np.squeeze(audio_block)
            buffer = np.concatenate((buffer[block_size - overlap_size:], audio_block))
            if np.abs(buffer).mean() >= MIC_THRESHOLD:
                yield buffer

def record(duration=3.0, samplerate=SAMPLERATE):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(audio)

def pitch_and_speed_shift(filename, semitones=PITCH_SEMITONES, speed_factor=PITCH_SPEED_FACTOR):
    sound = AudioSegment.from_file(filename)
    octaves = semitones / 12.0
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves) * speed_factor)
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(44100)
    play(pitched_sound)

async def speak(text, voice=VOICE, rate=SPEAK_RATE):
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await tts.save("output.mp3")
    pitch_and_speed_shift("output.mp3")

async def async_generator_wrapper(gen):
    for item in gen:
        yield item

async def listen_for_trigger():
    async for audio in async_generator_wrapper(stream_audio(SAMPLERATE)):
        text = await transcribe_async(audio)
        print("Heard:", text)
        if any(w.startswith(TRIGGER_WORD[:3]) for w in text.split()):
            return True
    return False

async def main_loop():
    print("Listening continuously...")
    cooldown_seconds = 5
    last_trigger_time = 0

    while True:
        current_time = time.time()
        if (current_time - last_trigger_time) < cooldown_seconds:
            # Cooldown aktiv, kleine Pause
            await asyncio.sleep(0.5)
            continue

        triggered = await listen_for_trigger()
        if triggered:
            last_trigger_time = time.time()
            print("Trigger word detected!")
            command_audio = record(duration=3.0)
            command = await transcribe_async(command_audio)
            print("Command:", command)
            response = "I do not understand."
            for key in responses:
                if key in command:
                    response = responses[key]
                    break
            print("Response:", response)
            await speak(response)
            if "stop" in command:
                print("Stopping...")
                break


if __name__ == "__main__":
    asyncio.run(main_loop())
