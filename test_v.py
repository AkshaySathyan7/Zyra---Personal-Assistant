import speech_recognition as sr

listener = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something...")
    voice = listener.listen(source)
    command = listener.recognize_google(voice)
    print("You said:", command)
