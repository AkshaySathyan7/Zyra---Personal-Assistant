import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import speech_recognition as sr

# ----------------------
# SETTINGS
# ----------------------
BOT_NAME = "zyra"   # wake word (optional in text mode)

# ----------------------
# INITIALIZE
# ----------------------
# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice

# Initialize speech recognition
recognizer = sr.Recognizer()

def talk(text):
    """Convert text to speech and print to console"""
    print("Zyra:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture speech input and convert to text"""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower().strip()
            print("You (speech):", command)
            return command
        except sr.WaitTimeoutError:
            talk("No speech detected. Please try again or use text input.")
            return None
        except sr.UnknownValueError:
            talk("Sorry, I couldn't understand the audio. Please try again or use text input.")
            return None
        except sr.RequestError:
            talk("Speech recognition service is unavailable. Please use text input.")
            return None

def get_input():
    """Prompt user to choose between text or speech input"""
    while True:
        talk("Would you like to use text or speech input? Type 'text' or 'speech'.")
        choice = input("You (input choice): ").lower().strip()
        if choice == "text":
            command = input("You (text): ").lower().strip()
            return command
        elif choice == "speech":
            command = listen()
            if command:
                return command
        else:
            talk("Invalid choice. Please type 'text' or 'speech'.")

def wish_me():
    """Greeting when starting"""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        talk("Good morning, I am Zyra, your personal assistant.")
    elif 12 <= hour < 18:
        talk("Good afternoon, I am Zyra, your personal assistant.")
    else:
        talk("Good evening, I am Zyra, your personal assistant.")
    talk("How can I help you today? Choose text or speech input.")

def run_zyra():
    """Main logic for Zyra using text or speech input"""
    command = get_input()

    if not command:
        return True  # Continue loop if no valid input

    if "play" in command:
        song = command.replace("play", "").strip()
        talk("Playing " + song)
        pywhatkit.playonyt(song)

    elif "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        talk("Current time is " + time)

    elif "who the heck is" in command:
        person = command.replace("who the heck is", "").strip()
        try:
            info = wikipedia.summary(person, 1)
            print(info)
            talk(info)
        except:
            talk("Sorry, I couldn’t find any information on that person.")

    elif "date" in command:
        talk("Sorry, I have a headache")

    elif "are you single" in command:
        talk("I am in a relationship with Wi-Fi")

    elif "joke" in command:
        talk(pyjokes.get_joke())

    elif command in ["exit", "quit", "bye"]:
        talk("Goodbye! Have a nice day.")
        return False  # Stop the loop

    else:
        talk("Please try the command again.")

    return True

# ----------------------
# MAIN PROGRAM
# ----------------------
if __name__ == "__main__":
    wish_me()
    while True:
        if not run_zyra():
            break