# 🌤️ WeatherGPT (SIH26068)
### Conversational AI for Weather Forecasting, Alerts, and Climate Information
**Ministry of Earth Sciences (MoES) | India Meteorological Department (IMD) | Theme: Disaster **

---

## 📌 Project Overview
**WeatherGPT** solves the **"last mile"** meteorological dissemination problem. India has vast amounts of weather data (IMD bulletins, Mausam app, Doppler radar, satellite imagery), but for an ordinary citizen, farmer, or traveler, this scatter technical data is difficult to interpret and act upon it and present it.

WeatherGPT provides an **authoritative, conversational AI layer** that:
1. Understands natural language voice and text queries in **Hindi, Hinglish, and English**.
2. Retrieves verified meteorological forecasts from **Open-Meteo & Numerical Weather Prediction (NWP)** models (ECMWF, GFS, ICON).
3. Evaluates severe weather thresholds and displays **NDMA SACHET / IMD CAP Early Warnings**.
4. Generates tailored, actionable domain advisories for **Farmers (Kisan 🌾)**, **Travelers (Yatri ✈️)**, **Urban Residents (Nagrik 🏙️)**, and **Disaster Officers (🚨)**.
5. **Prevents Hallucinations (Grounded AI)**: The AI never invents weather numbers; it only interprets and translates verified meteorological datasets.

---

## 🏗️ Architecture & Chat Flow

```
[1. User Query (Voice/Text)]
            │
            ▼
[2. Frontend (HTML5/CSS/JS + Voice Mic + Live Radar)]
            │ HTTP POST /api/chat
            ▼
[3. FastAPI Backend Engine]
            │
      ┌─────┴────────────────────────────┐
      ▼                                  ▼
[4. AI Layer (Gemini / NLU)]    [5. External Weather APIs]
 - Intent Detection              - Open-Meteo Realtime Forecast
 - Location & Time Extraction    - Multi-Model NWP (ECMWF/GFS/ICON)
                                 - NDMA SACHET / CAP Warning Feed
      │                                  │
      └──────────────┬───────────────────┘
                     ▼
[6. Python Advisory Engine]
 - Farmer: Irrigation, Spraying Window, Crop lodging
 - Traveler: Hydroplaning index, Fog visibility
 - Citizen: Heat stress, UV index, Umbrella alert
                     │
                     ▼
[7. Final Response Generation (Hindi / Hinglish / English)]
 - Grounded Explanation + Alert Badges + Visual Cards
```

---

## 🚀 Quick Start Guide

### 1. Run Backend (FastAPI)
The backend uses Python 3.12 managed via `uv`:

```bash
# Navigate to backend folder
cd weathergpt/backend

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\activate

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive API documentation (Swagger UI) is available at: **http://localhost:8000/docs**

### 2. Run Frontend
The frontend is a lightweight, mobile-first web app located in `weathergpt/frontend`.
Simply open `weathergpt/frontend/index.html` in any modern web browser (Google Chrome, Microsoft Edge, Brave) or serve it with any static server:

```bash
# Optional: using Python to serve frontend
cd weathergpt/frontend
python -m http.server 3000
```
Then visit **http://localhost:3000** in your browser.

---

## 🔑 Key Features Built

| Feature | Description |
|---|---|
| 🎙️ **Voice Recognition & Audio Playback** | Native Web Speech API for voice queries (Hindi/English mic) and Text-to-Speech (TTS) response reading. |
| 🛡️ **Grounded AI (Zero Hallucination)** | Strict separation between query understanding and meteorological facts. |
| 🧮 **NWP Model Comparison** | Side-by-side comparison across **ECMWF IFS-025**, **NOAA GFS**, and **DWD ICON**. |
| 🚨 **Disaster Alerts (NDMA/CAP)** | Automatic evaluation of rainfall, wind gusts, heatwaves, and thunderstorm warnings. |
| 🌾 **Domain Persona Modes** | Switch seamlessly between **Kisan (Farmer)**, **Yatri (Traveler)**, **Nagrik (Citizen)**, and **Disaster Officer**. |
| 🗺️ **Live Doppler Radar** | Leaflet-powered interactive precipitation radar map with RainViewer live tile overlays. |
| 📊 **Historical Climate Trends** | 5-Year rainfall and temperature trend analysis for regional planning. |

---

## 🎯 Winning Pitch for SIH Judges

### Q1: *"Mausam app already exists, why WeatherGPT?"*
> **Answer:** *"Mausam app and IMD portals are primarily one-way data display dashboards with raw numbers (e.g., 28°C, 82% humidity, 60% precipitation). WeatherGPT is an intelligent conversational layer that allows citizens to ask follow-up questions in their native language and receive contextual, decision-oriented advice—such as whether a farmer should irrigate their crops or a traveler should delay a road journey due to hydroplaning hazards."*

### Q2: *"How do you prevent the AI from hallucinating a wrong forecast?"*
> **Answer:** *"Our AI never predicts weather. We follow a strict Grounded Architecture: the LLM parses the user's intent and location, our deterministic backend fetches verified data from Open-Meteo and official early warning feeds, and the AI is strictly constrained to narrate that verified data in human-friendly language."*

### Q3: *"What is your production data source plan?"*
> **Answer:** *"For this rapid prototype, we use Open-Meteo and open meteorological APIs (zero-setup, global NWP models). In production, WeatherGPT is designed to integrate directly with IMD's official APIs and the Bharat Forecasting System (BFS) 6 km grid via MoES/NDMA CAP feeds."*

---

## 📂 Folder Structure

```
weathergpt/
├── backend/
│   ├── app/
│   │   ├── api/             # REST endpoints (chat, weather, alerts, climate)
│   │   ├── models/          # Pydantic data schemas
│   │   ├── services/        # Weather, Geocoding, Alerts, Advisory, AI engines
│   │   ├── config.py        # Settings & environment configuration
│   │   └── main.py          # FastAPI application entrypoint
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── css/style.css        # Glassmorphic responsive dark theme
│   ├── js/
│   │   ├── app.js           # UI & dashboard state controller
│   │   ├── chat.js          # Chat client & API communication
│   │   ├── voice.js         # STT Voice Mic & TTS audio playback
│   │   └── radar.js         # Leaflet Doppler precipitation radar
│   └── index.html           # Main user interface
└── README.md
```
