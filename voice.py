import os
import time
import datetime
import pygame
import webbrowser
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenRouter client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)
MODEL = os.getenv("MODEL")

recognizer = sr.Recognizer()

# ---------------------------
# 🔊 Text-to-Speech Function (Fixed for long replies)
# ---------------------------
import uuid

def speak(text):
    print("Zira:", text)
    try:
        # Split into smaller parts (max ~200 chars each)
        parts = [text[i:i+200] for i in range(0, len(text), 200)]
        pygame.mixer.init()

        for part in parts:
            # Use a unique filename every time
            filename = f"zira_reply_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=part, lang='en')
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Give Windows a short delay before deleting the file
            time.sleep(0.2)
            pygame.mixer.music.unload()
            os.remove(filename)

        pygame.mixer.quit()
    except Exception as e:
        print("Error in TTS:", e)

# ---------------------------
# 🎙️ Voice Input Function
# ---------------------------
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except Exception as e:
            print("Error while listening:", e)
            return ""

# ---------------------------
# ⏰ Alarm Function
# ---------------------------
def set_alarm(alarm_time):
    speak(f"Alarm set for {alarm_time}.")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            speak("Wake up! It's time!")
            break
        time.sleep(10)

# ---------------------------
# 🧠 Chat with OpenRouter
# ---------------------------
def chat_with_zira(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are Zira, a friendly AI voice assistant. Keep responses conversational and clear."},
                {"role": "user", "content": prompt}
            ],
            max_token=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error from API:", e)
        return "Sorry, I’m having trouble connecting right now."

# ---------------------------
# 🚀 Main Function
# ---------------------------
def main():
    speak("Hello! I am your AI voice assistant, Zira. How can I help you today?")

    while True:
        command = listen()
        if not command:
            continue

        if "stop" in command or "exit" in command or "quit" in command:
            speak("Goodbye! Have a great day!")
            break

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}.")

        elif "name" in command:
            speak("I am Zira, your personal voice assistant.")

        elif "open youtube" in command:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")

        elif "alarm" in command:
            speak("Please tell me the time for the alarm in 24-hour format, like 07:30 or 18:45.")
            alarm_time = listen()
            if alarm_time:
                set_alarm(alarm_time)
            else:
                speak("I couldn’t understand the time you said.")

        else:
            reply = chat_with_zira(command)
            speak(reply)

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    main()
