# Spotify AI Companion - Python Full Stack

A complete Python-based web application that connects to Spotify and uses Google Gemini AI to chat about your music taste!

## Features
- 🎵 Spotify OAuth authentication
- 💬 AI chat powered by Google Gemini
- 🎤 "Music Only Mode" - AI responds using only YOUR songs
- 📊 Personalized recommendations
- 🎨 Beautiful Spotify-inspired UI

## Setup Instructions

### 1. Install Dependencies
```bash
pip install flask flask-session requests google-generativeai
```

### 2. Create Project Structure
```
spotify-ai-companion/
├── app.py
├── requirements.txt
└── templates/
    ├── login.html
    └── index.html
```

### 3. Run the Application
```bash
python app.py
```

The app will start on: http://127.0.0.1:8000

### 4. First Time Setup
1. Visit http://127.0.0.1:8000
2. Click "Connect with Spotify"
3. Log in with your Spotify account
4. Grant permissions
5. You'll be redirected back and ready to chat!

## Configuration

All credentials are already configured in app.py:
- ✅ Spotify Client ID & Secret
- ✅ Google Gemini API Key
- ✅ Redirect URI set to http://127.0.0.1:8000/callback

## How It Works

1. **Authentication**: OAuth flow with Spotify to access your listening data
2. **Data Fetching**: Gets your recently played tracks, top artists, and top tracks
3. **AI Processing**: Google Gemini AI analyzes your music and responds naturally
4. **Music Only Mode**: Special mode where AI responds ONLY using your song library!

## Usage Tips

### Regular Mode:
- "What have I been listening to lately?"
- "Recommend me something new based on my taste"
- "What's my music vibe right now?"
- "Tell me about my top artists"

### Music Only Mode (Toggle ON):
- "How are you?" → Answers using your song lyrics!
- "What should I do today?" → Answers with song references!
- Ask ANYTHING and get answers made from your music!

## Features Breakdown

### 🎵 Spotify Integration
- Recently played tracks (last 50)
- Top artists (short term)
- Top tracks (short term)
- Automatic token refresh

### 🤖 Google Gemini AI
- Natural conversation about music
- Personalized recommendations
- Music Only Mode for creative responses
- Conversation history tracking

### 🎨 Beautiful UI
- Spotify-inspired dark theme
- Glassmorphism effects
- Real-time chat interface
- Quick action buttons
- Responsive design

## Troubleshooting

### "Not authenticated" error
- Make sure you've logged in with Spotify
- Try logging out and logging in again

### Token expired
- The app auto-refreshes tokens, but if it fails, just logout and login again

### Port already in use
- Change the port in app.py: `app.run(debug=True, port=8001)`
- Update redirect URI in Spotify Dashboard to match

### Gemini API errors
- Check your API key is valid
- Ensure you have API quota remaining

## Production Deployment

To deploy to production:

1. Update `SPOTIFY_REDIRECT_URI` to your domain
2. Update redirect URI in Spotify Developer Dashboard
3. Use environment variables for sensitive data:
```python
import os
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```
4. Use a production WSGI server (gunicorn, waitress)
5. Set `app.run(debug=False)`

## API Endpoints

- `GET /` - Main page
- `GET /login` - Initiate Spotify OAuth
- `GET /callback` - OAuth callback
- `GET /logout` - Logout
- `GET /api/user` - Get user info
- `GET /api/listening-history` - Get listening data
- `POST /api/chat` - Chat with AI
- `GET /api/recommendations` - Get Spotify recommendations

Enjoy your AI music companion! 🎵🤖