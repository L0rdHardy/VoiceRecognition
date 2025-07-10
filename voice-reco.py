import speech_recognition as sr

speech_engine = sr.Recognizer() # Initialize the recognizer here

def from_microphone():
    with sr.Microphone() as micro:
        print("Recording...")
        audio = speech_engine.record(micro, duration=5)
        print("Recognition...")
        try:
            text = speech_engine.recognize_google(audio, language="de-DE")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

# Assign the result of the function call to the 'text' variable
text = from_microphone()

print(text) # Print the recognized text

if text.lower() == "hallo": # Use .lower() for case-insensitive comparison
    print("Hallo, wie kann ich Ihnen helfen?")
else:
    print("Das habe ich nicht verstanden.")