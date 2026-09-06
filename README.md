# 🩺 AI Symptom Checker & Triage Assistant

An AI-powered medical triage application built with **Streamlit** and **Google Gemini 3.6 Flash**. Users enter symptoms and receive a structured triage recommendation — Self-Care, See a Doctor, or Emergency — along with possible conditions, red flags, and self-care tips.

---

## ✨ Features

- 🤖 **Gemini 3.6 Flash** — fast, accurate clinical language model
- 🟢🟠🔴 **3-tier triage** — Self-Care / See a Doctor / Emergency
- 📊 **Urgency score** (1–10) with visual progress bar
- 🔬 **Possible conditions** with Low / Moderate / High likelihood
- 🚨 **Red flags** that require immediate attention
- 💊 **Self-care tips** for manageable symptoms
- 📋 **Session history** in the sidebar
- ⬇️ **JSON export** of the full triage report
- 🔐 **API key** entered securely via sidebar (or `.env` file)

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
cd "Symptom Checker & Triage Assistant"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Gemini API key

**Option A — `.env` file (recommended):**

```bash
copy .env.example .env        # Windows
# or
cp .env.example .env          # macOS / Linux
```

Open `.env` and replace `your_gemini_api_key_here` with your actual key.

**Option B — Sidebar input:**  
Just paste the key directly into the sidebar when the app is running.

> Get a free API key at: https://aistudio.google.com/app/apikey

### 5. Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📁 Project Structure

```
Symptom Checker & Triage Assistant/
│
├── app.py               # Streamlit UI — all user interaction
├── symptom_engine.py    # Gemini 3.6 Flash integration & prompts
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .env                 # Your actual API key (git-ignored)
└── README.md            # This file
```

---

## 🔧 Configuration

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |

---

## ⚙️ How It Works

1. The user fills in symptoms, age, sex, duration, severity, history, and medications.
2. [`symptom_engine.py`](symptom_engine.py) formats a structured prompt and sends it to **Gemini 3.6 Flash** with a strict JSON schema.
3. The model returns a parsed JSON object with triage level, urgency score, conditions, red flags, and tips.
4. [`app.py`](app.py) renders the results using Streamlit metrics, expanders, progress bars, and colour-coded banners.

---

## ⚠️ Medical Disclaimer

This application provides **AI-generated informational guidance only**. It does **not** constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional. In a life-threatening emergency, **call 911 or your local emergency number immediately**.

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — Python-native web UI
- [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) — LLM backbone
- [google-genai](https://pypi.org/project/google-genai/) — Official Google GenAI Python SDK (v2+)
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable loading
