import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import speech_recognition as sr
import webbrowser
import requests
import random
import time

# ----------------------
# SETTINGS
# ----------------------
BOT_NAME = "zyra"
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your key
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"  # Replace with your key

# ----------------------
# INITIALIZE
# ----------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice
recognizer = sr.Recognizer()

# ----------------------
# FUNCTIONS
# ----------------------
def talk(text):
    """Speak and print simultaneously"""
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.25)  # tiny pause to prevent skipping
    print(f"{BOT_NAME.capitalize()}: {text}")

def listen():
    """Listen to speech input and return text"""
    mic_list = sr.Microphone.list_microphone_names()
    print("Available microphones:", mic_list)  # for debugging
    with sr.Microphone() as source:
        talk("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
            command = recognizer.recognize_google(audio).lower().strip()
            print("You (speech):", command)
            return command
        except sr.UnknownValueError:
            talk("Sorry, I couldn't understand you.")
            return None
        except sr.RequestError:
            talk("Speech recognition service is unavailable.")
            return None

def get_input_text():
    """Get text input from user"""
    return input("You (text): ").lower().strip()

def get_input_speech():
    """Get speech input from user until recognized"""
    while True:
        command = listen()
        if command:
            return command
        else:
            talk("Try speaking again...")

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            talk(f"Current temperature in {city} is {temp}°C with {desc}.")
        else:
            talk(f"Couldn't fetch weather for {city}.")
    except:
        talk("Weather service is currently unavailable.")

def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()
        articles = response.get("articles")
        if articles:
            talk("Here are the top 5 news headlines:")
            for i, article in enumerate(articles[:5], 1):
                talk(f"{i}. {article['title']}")
        else:
            talk("No news found.")
    except:
        talk("News service is currently unavailable.")

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        talk("Good morning! I am Zyra, your personal assistant.")
    elif 12 <= hour < 18:
        talk("Good afternoon! I am Zyra, your personal assistant.")
    else:
        talk("Good evening! I am Zyra, your personal assistant.")
    talk("Select your input mode: 1 for Text, 2 for Speech.")

# ---------------------- MAIN LOGIC ----------------------
def run_zyra(get_input_func):
    command = get_input_func()
    if not command:
        return True

    command_lower = command.lower()

    # --------- CASUAL CONVERSATION ----------
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in command_lower for word in greetings):
        talk("Hello! How are you today?")
        return True

    if "how are you" in command_lower or "how's it going" in command_lower:
        talk("I am just a bunch of code, but I'm doing great! How about you?")
        return True

    if "thank" in command_lower:
        talk("You're welcome!")
        return True

    if "what's up" in command_lower or "whats up" in command_lower:
        talk("Not much, just here to assist you! What about you?")
        return True

    if "i love you" in command_lower:
        talk("Aww, I love you too! But I am still a program 😄")
        return True

    # --------- FUN / ENTERTAINMENT ----------
    if "tell me something" in command_lower or "tell me a fact" in command_lower:
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts!",
            "Bananas are berries, but strawberries are not!",
            "A day on Venus is longer than a year on Venus."
        ]
        talk(random.choice(facts))
        return True

    if "joke" in command_lower:
        talk(pyjokes.get_joke())
        return True

    if "flip a coin" in command_lower:
        talk("Heads!" if random.randint(0,1) == 0 else "Tails!")
        return True

    if "roll a dice" in command_lower or "random number" in command_lower:
        num = random.randint(1,6) if "dice" in command_lower else random.randint(1,100)
        talk(f"Your random number is {num}")
        return True

    # --------- TIMER ----------
    if "set a timer for" in command_lower:
        try:
            words = command_lower.split()
            for i, word in enumerate(words):
                if word.isdigit():
                    seconds = int(word)
                    if i+1 < len(words) and "minute" in words[i+1]:
                        seconds *= 60
                    talk(f"Timer set for {seconds} seconds!")
                    time.sleep(seconds)
                    talk("Time's up!")
                    return True
            talk("Please specify the time in seconds or minutes.")
        except:
            talk("I couldn't set the timer. Try again.")
        return True

    # --------- MATH ----------
    if "add" in command_lower or "plus" in command_lower:
        nums = [int(s) for s in command_lower.split() if s.isdigit()]
        if len(nums) >= 2:
            talk(f"The answer is {sum(nums)}")
        else:
            talk("Please provide two numbers to add.")
        return True

    if "subtract" in command_lower or "minus" in command_lower:
        nums = [int(s) for s in command_lower.split() if s.isdigit()]
        if len(nums) >= 2:
            talk(f"The answer is {nums[0] - nums[1]}")
        else:
            talk("Please provide two numbers to subtract.")
        return True

    if "multiply" in command_lower or "times" in command_lower:
        nums = [int(s) for s in command_lower.split() if s.isdigit()]
        if len(nums) >= 2:
            talk(f"The answer is {nums[0] * nums[1]}")
        else:
            talk("Please provide two numbers to multiply.")
        return True

    if "divide" in command_lower or "divided by" in command_lower:
        nums = [int(s) for s in command_lower.split() if s.isdigit()]
        if len(nums) >= 2:
            if nums[1] == 0:
                talk("Cannot divide by zero!")
            else:
                talk(f"The answer is {nums[0] / nums[1]}")
        else:
            talk("Please provide two numbers to divide.")
        return True

    # --------- STANDARD COMMANDS ----------
    if "play" in command_lower:
        song = command_lower.replace("play", "").strip()
        talk("Playing " + song)
        pywhatkit.playonyt(song)
        return True

    elif "time" in command_lower:
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        talk("Current time is " + time_str)
        return True

    elif "date" in command_lower:
        date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
        talk("Today is " + date_str)
        return True

    elif "who is" in command_lower or "who the heck is" in command_lower:
        person = command_lower.replace("who is", "").replace("who the heck is", "").strip()
        try:
            info = wikipedia.summary(person, sentences=1)
            talk(info)
        except wikipedia.exceptions.DisambiguationError:
            talk(f"Multiple results found for {person}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            talk(f"Sorry, I couldn't find information about {person}.")
        return True

    elif "open" in command_lower:
        if "youtube" in command_lower:
            webbrowser.open("https://www.youtube.com")
            talk("Opening YouTube")
        elif "google" in command_lower:
            webbrowser.open("https://www.google.com")
            talk("Opening Google")
        else:
            site = command_lower.replace("open", "").strip()
            url = "https://" + site
            webbrowser.open(url)
            talk(f"Opening {site}")
        return True

    elif "weather" in command_lower:
        city = command_lower.replace("weather", "").strip()
        if city:
            get_weather(city)
        else:
            talk("Please specify the city.")
        return True

    elif "news" in command_lower:
        get_news()
        return True

    elif "are you single" in command_lower:
        talk("I am in a relationship with Wi-Fi.")
        return True

    elif "remind me" in command_lower:
        reminder = command_lower.replace("remind me", "").strip()
        talk(f"Reminder set: {reminder}. Don't forget!")
        return True

    elif command_lower in ["exit", "quit", "bye"]:
        talk("Goodbye! Have a nice day.")
        return False

    # --------- FALLBACK ----------
    talk("I didn't understand that. Try another command.")
    return True

# ----------------------
# MAIN PROGRAM
# ----------------------
if __name__ == "__main__":
    wish_me()
    while True:
        mode = input("Enter 1 for Text, 2 for Speech: ").strip()
        if mode == "1":
            get_input_func = get_input_text
            talk("Text mode selected. Let's start!")
            break
        elif mode == "2":
            get_input_func = get_input_speech
            talk("Speech mode selected. Let's start!")
            break
        else:
            talk("Invalid choice. Enter 1 or 2.")

    continue_chat = True
    while continue_chat:
        continue_chat = run_zyra(get_input_func)
        if continue_chat:
            talk("What would you like me to do next?")
