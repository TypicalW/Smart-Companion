Main file is test.py

# 🎙️ AI Voice Assistant - Zira

An intelligent voice assistant built in Python that listens, speaks, and performs tasks like opening websites, setting alarms, and chatting through AI (OpenRouter/OpenAI API).

---

## 🚀 Features
- Voice input using `speech_recognition`
- Natural voice replies using `gTTS` + `pygame`
- Integration with OpenRouter / OpenAI API (GPT-4o-mini)
- Opens YouTube, Google, and Wikipedia
- Sets alarms and gives time-based reminders
- Offline fallback speech via `pyttsx3`

---

## 🧠 Tech Stack
- **Python 3.12+**
- **Libraries**: `SpeechRecognition`, `gTTS`, `pygame`, `pyttsx3`, `openai`, `python-dotenv`
- **AI Model**: `gpt-4o-mini` via OpenRouter

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-voice-assistant.git
cd ai-voice-assistant

2️⃣ Create Virtual Environment
python -m venv ai1
.\ai1\Scripts\Activate.ps1

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Environment Variables

Create a file named .env in the project root:

BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=your_openrouter_key_here
MODEL=gpt-4o-mini

5️⃣ Run the Assistant
python test.py

🗣️ Example Commands

“Open YouTube”

“Set alarm for 07:30”

“Tell me about World War 1”

“Who is Virat Kohli”

“Stop”

👩‍💻 Author

Aanandi
GitHub: @aanandi2004

🧾 License

This project is open-source under the MIT License
.


---

### **2️⃣ Add and Commit Everything**

Run these commands in PowerShell:

```powershell
git add .
git commit -m "Initial commit: AI Voice Assistant Zira"
