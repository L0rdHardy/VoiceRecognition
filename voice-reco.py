import speech_recognition as sr
import pyttsx3

speech_engine = sr.Recognizer() # Initialize the recognizer here
engine = pyttsx3.init() # Initialize the text-to-speech engine

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
    engine.say("Hallo, wie kann ich Ihnen helfen?")
    engine.runAndWait()
else:
    engine.say("Ich habe Sie nicht verstanden.")
    engine.runAndWait()