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
            text = speech_engine.recognize_google(audio, language="en-US")
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

if text.lower() == "hello": # Use .lower() for case-insensitive comparison
    engine.say("Hello, how can i help you?")
    engine.runAndWait()
else:
    engine.say("I did not understand you.")
    engine.runAndWait()