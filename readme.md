# To-Do
- Voice activation (via Button)<br>
- Voice recognition via AI (whisper oder so)<br>
- Voice Commands <br>
-- Voice Output<br>
-- Actions via GPIO Pins<br>
- Face recognition (15 FPs)<br>
- Motorsteuerung via GPIO Pins<br>

---

# Voice Command AI with Whisper & edge-tts

This Python script enables voice-controlled interaction using a trigger word and subsequent command processing. It uses OpenAI Whisper for speech recognition and Microsoft edge-tts for speech synthesis. The voice output can be modulated in pitch and speed.

---

## Features

- Detect a custom trigger word via microphone (default: "yorick")
- Record audio with automatic silence detection
- Speech recognition using Whisper model (`large-v3` by default)
- Text-to-speech with edge-tts (Microsoft Neural Voices)
- Adjustable pitch and speed for speech output
- Simple command processing with example responses
- Stop command to exit the program

---

## Requirements

- Python 3.8+
- GPU recommended for Whisper, CPU also supported
- Working microphone on Windows/Linux/macOS

---

## Installation

1. Prepare a Python virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    venv\Scripts\activate      # Windows
    ```

2. Install dependencies:

    ```bash
    pip install torch sounddevice numpy pydub whisper edge-tts soundfile
    ```

3. Install `ffmpeg` and ensure it's in your system PATH (required by pydub):

    - Windows: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
    - Linux: e.g. `sudo apt install ffmpeg`  
    - macOS: `brew install ffmpeg`

---

## Usage

Run the script:

    ```bash
    python your_script_name.py
    ```

Speak the trigger word ("yorick"), followed by a command.

### Example commands:

- Saying `"stop"` will terminate the program.
- Other commands prompt to "Try again, human."

---

## Configuration

Adjust parameters at the top of the script as needed:

    ```python
    trigger_word = "yorick"
    speak_rate = "+50%"
    speak_deepnes = -8      # pitch shift in semitones
    speak_speed = 1.0       # normal speed
    record_duration = 2.0   # seconds to record for trigger word
    command_duration = 3.0  # seconds to record for command
    mic_threshold = 0.02    # silence threshold
    model_size = "large-v3" # Whisper model size (smaller models run faster)
    ```

---

## Notes

- Speech recognition language is set to English (`language="en"`).
- Adjust `mic_threshold` according to your ambient noise level.
- Performance depends on hardware; GPU speeds up Whisper considerably.
- Pitch shifting uses `pydub`, consider other libraries for real-time or high-performance needs.

---
