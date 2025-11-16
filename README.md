# Morbus

Morbus is your personal AI music companion.  
It connects to your Spotify, understands what you actually listen to, and talks to you like a friend who knows your music taste inside-out.

It reads your recent tracks, your top artists, your top songs—and uses them to generate smart, personal, music-driven conversations.  
There’s also **Music-Only Mode**, where Morbus replies using ONLY your own songs, lyrics, or artists.  
No fake stuff. No random songs. Just *you*.

# Features

- Spotify login (OAuth)
- Reads your recent listening history
- Shows your top artists and top tracks
- Friendly AI chat powered by OpenAI
- Music-Only Mode using your actual Spotify library
- Smart Spotify recommendations
- Clean `.env` configuration for secrets
- Fully ready for Render deployment

# Tech Stack

- Python (Flask)
- Spotify Web API
- OpenAI API
- Flask-Session
- python-dotenv
- gunicorn

# Installation

## 1. Clone the project
git clone https://github.com/saakshammm/morbus.git
cd morbus

## 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

## 3. Install all dependencies
pip install -r requirements.txt

## 4. Create your .env file
OPENAI_API_KEY=your_openai_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
SECRET_KEY=your_flask_secret_key

## 5. Run Morbus
python app.py

# Local server
http://127.0.0.1:8000

# What is Morbus?

Morbus is dark, minimal, and aware of your taste.  
It doesn't just see your music — it *understands* your mood, your vibe, your patterns.  
Think of it as a shadowy music companion that speaks your sonic language.
