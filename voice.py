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
MODEL = os.getenv("MODEL", "gpt-4o-mini")

recognizer = sr.Recognizer()

# ---------------------------
# Context Memory Configuration
# ---------------------------
# Number of previous exchanges to keep (each exchange consists of user + assistant)
MAX_CONTEXT_EXCHANGES = 3  # stores up to 3 past exchanges => ~6 messages
context = []  # list of messages in OpenAI chat format: {"role": "user"/"assistant", "content": "..."}

# ---------------------------
#  Text-to-Speech Function (Fixed for Long Replies)
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

            # Give OS a short delay before deleting the file
            time.sleep(0.2)
            pygame.mixer.music.unload()
            os.remove(filename)

        pygame.mixer.quit()
    except Exception as e:
        # If gTTS/pygame fails, fallback to printing and continue
        print("Error in TTS:", e)

# ---------------------------
#  Voice Input Function
# ---------------------------
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
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
# Alarm Function
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
# Context memory helpers
# ---------------------------
def append_to_context(role, content):
    """
    Append a role-message to context and ensure we keep only the last N exchanges.
    role: 'user' or 'assistant'
    content: string
    """
    global context
    context.append({"role": role, "content": content})
    # Trim context to keep at most MAX_CONTEXT_EXCHANGES * 2 messages (user+assistant)
    max_messages = MAX_CONTEXT_EXCHANGES * 2
    if len(context) > max_messages:
        # keep the last max_messages entries
        context = context[-max_messages:]

def clear_context():
    global context
    context = []

# ---------------------------
# Chat with OpenRouter (with context)
# ---------------------------
SYSTEM_PROMPT = "You are Zira, a friendly AI voice assistant. Keep responses conversational and clear."

def chat_with_zira(prompt):
    """
    Build the messages with system prompt + context + current user prompt, then query API.
    """
    try:
        # Build messages list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Append stored context (if any)
        if context:
            messages.extend(context)

        # Append current user message
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=500
        )

        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        print("Error from API:", e)
        return "Sorry, I’m having trouble connecting right now."

# ---------------------------
#  Main Function
# ---------------------------
def main():
    speak("Hello! I am your AI voice assistant, Zira. How can I help you today?")

    while True:
        command = listen()
        if not command:
            continue

        # Allow user to clear or check memory
        if "clear memory" in command or "forget" in command:
            clear_context()
            speak("Context memory cleared.")
            continue

        if "show memory" in command or "what did we talk about" in command:
            if not context:
                speak("There is no context memory stored yet.")
            else:
                # Summarize last interactions briefly for the user
                summary = []
                for msg in context:
                    role = "You" if msg["role"] == "user" else "Zira"
                    # show only short snippets
                    snippet = msg["content"][:120].replace("\n", " ")
                    summary.append(f"{role}: {snippet}")
                speak("Recent conversation snippets: " + " ; ".join(summary))
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
            # 1) Append user message to context (so the model sees it as part of dialogue)
            append_to_context("user", command)

            # 2) Get reply from model (context-aware)
            reply = chat_with_zira(command)

            # 3) Append assistant reply to context
            append_to_context("assistant", reply)

            # 4) Speak the reply
            speak(reply)

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    main()
