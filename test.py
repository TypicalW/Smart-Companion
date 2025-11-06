import os
import time
import webbrowser
import pygame
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv
import uuid

# ---------------- Setup ---------------- #
load_dotenv()
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)
MODEL = os.getenv("MODEL")


engine = pyttsx3.init()
engine.setProperty('rate', 180)  # speech speed
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)  # usually female voice

# ---------------- Speaking Function ---------------- #
def speak(text):
    print("Zira:", text)
    try:
        parts = [text[i:i+180] for i in range(0, len(text), 180)]
        pygame.mixer.init()

        for part in parts:
            filename = f"zira_reply_{uuid.uuid4().hex}.mp3"
            try:
                # Try generating online TTS
                tts = gTTS(text=part, lang='en')
                tts.save(filename)
            except Exception as e:
                print("⚠️ gTTS failed, using offline pyttsx3:", e)
                pygame.mixer.quit()
                engine.say(part)
                engine.runAndWait()
                continue

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            time.sleep(0.2)
            pygame.mixer.music.unload()
            os.remove(filename)

        pygame.mixer.quit()

    except Exception as e:
        print("Error in TTS:", e)

# ---------------- Listening Function ---------------- #
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError:
            print("Speech Recognition service error.")
            return ""

# ---------------- Actions ---------------- #
def set_alarm(alarm_time):
    speak(f"Alarm set for {alarm_time}")
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == alarm_time:
            speak("Wake up! It's time!")
            break
        time.sleep(10)

def open_website(command):
    if "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
    elif "google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
    elif "wikipedia" in command:
        webbrowser.open("https://www.wikipedia.org")
        speak("Opening Wikipedia.")
    else:
        speak("I’m not sure which website you want to open.")

# ---------------- AI Response ---------------- #
def chat_with_zira(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Zira, a friendly voice assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        return reply
    except Exception as e:
        return f"Error fetching response: {e}"

# ---------------- Main Loop ---------------- #
def main():
    speak("Hello! I am your AI voice assistant, Zira. How can I help you today?")

    while True:
        command = listen()
        if not command:
            continue

        if "exit" in command or "stop" in command:
            speak("Goodbye! Have a nice day.")
            break

        elif "open" in command:
            open_website(command)

        elif "set alarm" in command:
            speak("Please tell me the time for the alarm in 24-hour format, like 07:30 or 18:45.")
            alarm_time = listen()
            if alarm_time:
                set_alarm(alarm_time)
            else:
                speak("I couldn’t understand the time you said.")

        else:
            reply = chat_with_zira(command)
            speak(reply)

# ---------------- Run ---------------- #
if __name__ == "__main__":
    main()
