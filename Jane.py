#!/usr/bin/env python3
# Requires PyAudio and SpeechRecognition
# Requires a contacts.txt file with each line containing a name and phone number separated by a space

import speech_recognition as sr
import time
import os
import subprocess
import webbrowser
from gtts import gTTS

CONFIG_FILE = "config.txt"
CONTACTS_FILE = "contacts.txt"
AUDIO_FILE = "audio.mp3"

def read_file(name):
    try:
        with open(name, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

def write_file(name, content):
    with open(name + ".txt", 'w') as file:
        for line in content:
            file.write(line + "\n")

def load_configurations():
    default_config = ["Tim", "Jane"]
    config = read_file(CONFIG_FILE)
    if not config:
        write_file(CONFIG_FILE, default_config)
        return default_config
    return config

def speak(text):
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang='en')
    tts.save(AUDIO_FILE)
    subprocess.run(["mpg123", AUDIO_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(AUDIO_FILE)  # Clean up temporary audio file

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            speak("I couldn't understand you.")
        except sr.RequestError:
            speak("Error connecting to the speech recognition service.")
        except sr.WaitTimeoutError:
            speak("I didn't hear anything.")
    return ""

def send_sms():
    try:
        with open(CONTACTS_FILE, 'r') as file:
            contacts = [line.strip().split(" ", 1) for line in file.readlines()]
    except FileNotFoundError:
        speak("Contacts file not found.")
        return

    if not contacts:
        speak("No contacts available.")
        return

    for index, (name, number) in enumerate(contacts):
        print(f"{index}: {name} - {number}")

    speak("Select a contact by number.")
    try:
        contact_index = int(record_audio())
        if 0 <= contact_index < len(contacts):
            recipient = contacts[contact_index][1]
            speak("Record your message.")
            message = record_audio()
            speak(f"Would you like to send '{message}' to {contacts[contact_index][0]}?")
            confirmation = record_audio()
            if "yes" in confirmation:
                subprocess.run(["kdeconnect-cli", "--send-sms", message, "-n", "s20", "--destination", recipient])
                speak("Message sent.")
        else:
            speak("Invalid selection.")
    except ValueError:
        speak("Invalid input.")

def assistant(name, command):
    if f"{name} how are you" in command:
        print("how are you?")
        speak("I am fine, thanks.")
    elif any(phrase in command for phrase in [f"{name} see you later", f"bye {name}", f"{name} bye","bye"]):
        print("exit")
        exit()
    elif f"{name} what time is it" in command:
        speak(time.ctime())
    elif f"{name} where is" in command:
        location = command.split(" ", 2)[-1]
        speak(f"Hold on, I will show you where {location} is.")
        webbrowser.open_new_tab(f"https://www.google.com/maps/place/{location}")
    elif f"{name}search for" in command:
        search_query = command.split(" ", 2)[-1]
        speak(f"Searching for {search_query}.")
        webbrowser.open_new_tab(f"http://www.google.com/search?q={search_query}")
    elif f"{name} start" in command:
        program = command.split(" ", 1)[-1].lower()
        speak(f"Starting {program}")
        subprocess.Popen(program, shell=True)
    elif f"{name} signal" in command:
        subprocess.Popen("signal-desktop", shell=True)
    elif f"hey {name}" in command:
        speak("Hey, what's up?")
    elif f"{name} send text" in command:
        send_sms()
    elif f"{name} open instagram" in command:
        subprocess.Popen("instagram", shell=True)
    elif "configuration" in command:
        config_menu()

def config_menu():
    options = """
    1) Change your username
    2) What do you want to call me?
    3) Go back
    """
    speak(options)

    config = load_configurations()
    while True:
        choice = record_audio()
        if choice in ["1", "change your username"]:
            speak("What is your new username?")
            new_name = record_audio()
            if new_name:
                speak(f"Confirm: {new_name}? Say 'yes' to confirm.")
                if "yes" in record_audio():
                    config[0] = new_name
                    speak(f"Nice to meet you again, {new_name}.")
                    break
        elif choice in ["2", "what do you want to call me"]:
            speak("What do you want to call me?")
            new_assistant_name = record_audio()
            if new_assistant_name:
                speak(f"Confirm: {new_assistant_name}? Say 'yes' to confirm.")
                if "yes" in record_audio():
                    config[1] = new_assistant_name
                    speak(f"I like that name, {new_assistant_name}.")
                    break
        elif choice in ["3", "go back"]:
            speak("Returning to main menu.")
            break
        else:
            speak("Invalid choice. Try again.")

    write_file(CONFIG_FILE, config)

def banner():
    print("""
     _                                 Virtual
    | | __ _ _ __   ___   _ __  _   _  Assistant
 _  | |/ _` | '_ \ / _ \ | '_ \| | | |
| |_| | (_| | | | |  __/_| |_) | |_| |
 \___/ \__,_|_| |_|\___(_) .__/ \__, |
                         |_|    |___/ 
    """)

def main():
    banner()
    config = load_configurations()
    speak(f"Hi {config[0]}, I am {config[1]}. How can I help?")
    while True:
        command = record_audio()
        print(command)
        if command:
            assistant(config[1], command)
        print(command)
if __name__ == "__main__":
    main()
