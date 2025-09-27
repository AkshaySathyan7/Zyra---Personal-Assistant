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
import threading
import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, Label, Entry, Button, BOTH, LEFT, RIGHT, Y, END, StringVar, OptionMenu, TOP, BOTTOM

BOT_NAME = "Zyra"
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
recognizer = sr.Recognizer()
selected_mic_index = None
input_mode = "both"

root = tk.Tk()
root.title("Zyra Voice Assistant")
root.geometry("500x650")
root.resizable(False, False)

canvas = Canvas(root, bg="#F5F5F5")
scrollbar = Scrollbar(root, command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#F5F5F5")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side=TOP, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

entry_frame = Frame(root, bg="#DDDDDD")
entry_frame.pack(side=BOTTOM, fill="x", padx=5, pady=5)
user_input = Entry(entry_frame, font=("Arial", 14))
user_input.pack(side=LEFT, fill="x", expand=True, padx=5)
send_btn = Button(entry_frame, text="Send", command=lambda: threading.Thread(target=send_message).start())
send_btn.pack(side=LEFT, padx=5)
mic_btn = Button(entry_frame, text="🎤 Speak", command=lambda: threading.Thread(target=speak_message).start())
mic_btn.pack(side=LEFT, padx=5)

def add_message(sender, text):
    bubble_color = "#DCF8C6" if sender == BOT_NAME else "#ECECEC"
    anchor_side = "w" if sender == BOT_NAME else "e"
    bubble = Frame(scrollable_frame, bg=scrollable_frame["bg"], padx=10, pady=5)
    bubble.pack(anchor=anchor_side, pady=5, padx=10, fill="x")
    label = Label(bubble, text=text, bg=bubble_color, wraplength=350, justify="left",
                  font=("Arial", 12), bd=5, relief="ridge", padx=8, pady=4, cursor="hand2")
    label.pack(anchor=anchor_side, fill="none")
    def open_url(event):
        if text.startswith("http"):
            webbrowser.open(text)
    label.bind("<Button-1>", open_url)
    canvas.update_idletasks()
    canvas.yview_moveto(1)

def talk(text):
    if input_mode in ["speech", "both"]:
        engine.say(text)
        engine.runAndWait()
    add_message(BOT_NAME, text)

def get_input_text():
    return user_input.get().strip()

def get_input_speech():
    global selected_mic_index
    if selected_mic_index is None:
        talk("Please select a microphone first!")
        return None
    try:
        with sr.Microphone(device_index=selected_mic_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            add_message(BOT_NAME, "Listening...")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
            command = recognizer.recognize_google(audio).strip()
            add_message("You", command)
            return command
    except:
        talk("Sorry, I couldn't understand you.")
        return None

def send_message():
    if input_mode in ["text", "both"]:
        command = get_input_text()
        if not command: return
        user_input.delete(0, END)
        add_message("You", command)
        threading.Thread(target=zyra_response, args=(command,)).start()

def speak_message():
    if input_mode in ["speech", "both"]:
        threading.Thread(target=lambda: zyra_response(get_input_speech())).start()

def set_mode(mode):
    global input_mode
    input_mode = mode
    mode_frame.destroy()
    if mode in ["speech", "both"]:
        show_mic_selection()
    talk(f"{mode.capitalize()} mode selected. You can start chatting now.")

def show_mic_selection():
    global mic_frame, selected_mic_index
    mic_frame = tk.Frame(root, bg="#DDDDDD")
    mic_frame.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(mic_frame, text="Select Microphone:", font=("Arial", 14), bg="#DDDDDD").pack(pady=5)
    mic_list = sr.Microphone.list_microphone_names()
    mic_var = StringVar(root)
    mic_var.set(mic_list[0])
    dropdown = OptionMenu(mic_frame, mic_var, *mic_list)
    dropdown.pack(pady=5)
    def select_mic():
        nonlocal mic_var
        selected_mic_index = mic_list.index(mic_var.get())
        mic_frame.destroy()
        talk(f"Microphone '{mic_var.get()}' selected. You can start speaking now!")
    tk.Button(mic_frame, text="Select", command=select_mic).pack(pady=5)

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
        talk("Weather service is unavailable.")

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
        talk("News service is unavailable.")

def get_time_dynamic(location):
    try:
        location_clean = location.lower().replace("time in","").strip().replace(" ","%20")
        url = f"http://worldtimeapi.org/api/timezone"
        all_zones = requests.get(url).json()
        matched = [tz for tz in all_zones if location_clean in tz.lower()]
        if matched:
            tz_url = f"http://worldtimeapi.org/api/timezone/{matched[0]}"
            res = requests.get(tz_url).json()
            datetime_str = res["datetime"]
            time_only = datetime_str.split("T")[1].split(".")[0]
            hour_min = ":".join(time_only.split(":")[:2])
            return f"Current time in {matched[0]} is {hour_min}"
        else:
            return "Current time in India is "+datetime.datetime.now().strftime("%I:%M %p")
    except:
        return "Sorry, could not fetch time."

def zyra_response(command):
    if not command: return
    cmd = command.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in cmd for word in greetings):
        talk("Hello! How are you today?")
        return
    if "i am fine" in cmd or "i'm fine" in cmd:
        talk("Good to hear!")
        return
    if "how are you" in cmd:
        talk("I am a program, but I am doing great! How about you?")
        return
    if "thank" in cmd:
        talk("You're welcome!")
        return
    if "joke" in cmd:
        talk(pyjokes.get_joke())
        return
    if "flip a coin" in cmd:
        talk("Heads!" if random.randint(0,1)==0 else "Tails!")
        return
    if "roll a dice" in cmd or "random number" in cmd:
        num = random.randint(1,6) if "dice" in cmd else random.randint(1,100)
        talk(f"Your random number is {num}")
        return
    if "tell me something" in cmd or "tell me a fact" in cmd:
        facts = [
            "Honey never spoils.",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not.",
            "A day on Venus is longer than a year on Venus."
        ]
        talk(random.choice(facts))
        return
    if "time" in cmd:
        talk(get_time_dynamic(cmd))
        return
    if "date" in cmd:
        talk("Today is "+datetime.datetime.now().strftime("%A, %B %d, %Y"))
        return
    if "weather" in cmd:
        city = cmd.replace("weather", "").strip()
        if city: get_weather(city)
        else: talk("Please specify the city.")
        return
    if "news" in cmd:
        get_news()
        return
    if "play" in cmd:
        song = cmd.replace("play","").strip()
        talk("Playing "+song)
        pywhatkit.playonyt(song)
        return
    if "open" in cmd:
        site = cmd.replace("open","").strip()
        if "youtube" in cmd: site = "https://www.youtube.com"
        elif "google" in cmd: site = "https://www.google.com"
        elif not site.startswith("http"): site = "https://" + site
        webbrowser.open(site)
        talk(f"Opening {site}")
        return
    if cmd in ["exit","quit","bye"]:
        talk("Goodbye! Have a nice day.")
        root.quit()
        return

    talk("I didn't understand that. Try another command.")

mode_frame = tk.Frame(root, bg="#DDDDDD")
mode_frame.place(relx=0.5, rely=0.5, anchor="center")
tk.Label(mode_frame, text="Select Input Mode:", font=("Arial", 16), bg="#DDDDDD").pack(pady=5)
tk.Button(mode_frame, text="Text Only", width=25, command=lambda: set_mode("text")).pack(pady=5)
tk.Button(mode_frame, text="Speech Only", width=25, command=lambda: set_mode("speech")).pack(pady=5)
tk.Button(mode_frame, text="Both (Text + Speech)", width=25, command=lambda: set_mode("both")).pack(pady=5)

talk("Hello! I am Zyra. Please select your input mode to start chatting.")
root.mainloop()
