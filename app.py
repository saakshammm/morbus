from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session # type: ignore
import requests
from datetime import datetime, timedelta
import base64
from openai import OpenAI # type: ignore
from openai_config import OPENAI_API_KEY
from spotify_config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spotify-ai-companion-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# Spotify Configuration
auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
SCOPE = 'user-read-recently-played user-top-read user-read-playback-state user-read-currently-playing'

# OpenAI Configuration
client = OpenAI(api_key=OPENAI_API_KEY)

def get_auth_header():
    """Get Spotify authorization header"""
    if 'token_info' not in session:
        return None
    
    token_info = session['token_info']
    
    # Check if token is expired
    now = int(datetime.now().timestamp())
    is_expired = token_info.get('expires_at', 0) - now < 60
    
    if is_expired:
        token_info = refresh_access_token(token_info.get('refresh_token'))
        if token_info:
            session['token_info'] = token_info
    
    return {'Authorization': f"Bearer {token_info['access_token']}"}

def refresh_access_token(refresh_token):
    """Refresh Spotify access token"""
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        token_info['expires_at'] = int(datetime.now().timestamp()) + token_info['expires_in']
        return token_info
    return None

@app.route('/')
def index():
    """Main page"""
    if 'token_info' not in session:
        return render_template('login.html')
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Spotify OAuth"""
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': SCOPE
    }
    
    auth_url = f"{SPOTIFY_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Spotify OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('index'))
    
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }
    
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        token_info['expires_at'] = int(datetime.now().timestamp()) + token_info['expires_in']
        session['token_info'] = token_info
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/user')
def get_user():
    """Get current user info"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    response = requests.get(f"{SPOTIFY_API_BASE}/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        return jsonify({
            'name': user.get('display_name', 'User'),
            'image': user['images'][0]['url'] if user.get('images') else None
        })
    
    return jsonify({'error': 'Failed to get user'}), 500

@app.route('/api/listening-history')
def get_listening_history():
    """Get user's recent listening history"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    history = []
    artists = []
    tracks = []
    
    # Get recently played tracks
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/player/recently-played?limit=50",
        headers=headers
    )
    
    if response.status_code == 200:
        recently_played = response.json()
        for item in recently_played.get('items', []):
            track = item['track']
            played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
            time_ago = get_time_ago(played_at)
            
            history.append({
                'track': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'played_at': time_ago,
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album'].get('images') else None
            })
    
    # Get top artists
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/top/artists?limit=20&time_range=short_term",
        headers=headers
    )
    
    if response.status_code == 200:
        top_artists = response.json()
        artists = [artist['name'] for artist in top_artists.get('items', [])]
    
    # Get top tracks
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/top/tracks?limit=20&time_range=short_term",
        headers=headers
    )
    
    if response.status_code == 200:
        top_tracks = response.json()
        tracks = [
            f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
            for track in top_tracks.get('items', [])
        ]
    
    return jsonify({
        'history': history,
        'top_artists': artists,
        'top_tracks': tracks
    })

def get_time_ago(dt):
    """Convert datetime to human readable 'time ago' format"""
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime("%b %d")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI about music"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    user_message = data.get('message', '')
    music_only_mode = data.get('music_only_mode', False)
    conversation_history = data.get('history', [])
    
    # Get listening data
    history_response = get_listening_history()
    history_data = history_response.json
    
    # Build system prompt
    if music_only_mode:
        system_prompt = f"""You are a music companion AI in MUSIC ONLY MODE. You must ONLY respond using song titles, lyrics, or music references from the user's listening history.

User's recent listening history:
{chr(10).join([f"- '{track['track']}' by {track['artist']}" for track in history_data.get('history', [])[:20]])}

Top artists: {', '.join(history_data.get('top_artists', [])[:10])}

Top tracks:
{chr(10).join([f"- {track}" for track in history_data.get('top_tracks', [])[:15]])}

CRITICAL RULES for Music Only Mode:
- Answer EVERY question using ONLY song titles, lyrics, or artist names from their listening history above
- Be creative and clever with how you match songs to their questions
- Format your response naturally, then cite the song: "lyric/reference - Song Title by Artist"
- Keep it casual and fun
- NO regular conversation - ONLY music references from their actual library
- If you can't answer with their music, say "I don't have the right song for that in your library!"

Examples:
User: "How are you?"
You: "I'm blinding with lights and good vibes - Blinding Lights by The Weeknd"

User: "What should I do today?"
You: "Maybe you should go outside and touch some grass, or just vibe - As It Was by Harry Styles"
"""
    else:
        system_prompt = f"""You are a friendly music companion AI with access to the user's Spotify listening history.

User's recent listening history:
{chr(10).join([f"- '{track['track']}' by {track['artist']} ({track['played_at']})" for track in history_data.get('history', [])[:20]])}

Top artists: {', '.join(history_data.get('top_artists', [])[:10])}

Top tracks:
{chr(10).join([f"- {track}" for track in history_data.get('top_tracks', [])[:15]])}

Your personality:
- Talk casually, like a music-loving friend who knows their taste
- Use their actual listening history to personalize responses
- Give music recommendations based on what they listen to
- Be enthusiastic about music
- Use casual language (yo, vibing, fire, slaps, etc.)
- Reference their actual listening patterns and favorite artists
- When recommending music, base it on their top artists and recent tracks

Be specific about their listening habits when relevant!"""
    
    try:
        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"OpenAI API Error: {error_msg}")
        
        return jsonify({
            'error': f'AI Error: {error_msg}',
            'response': "Sorry, I'm having trouble connecting to the AI. Try again?"
        }), 200

@app.route('/api/recommendations')
def get_recommendations():
    """Get Spotify recommendations"""
    headers = get_auth_header()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get user's top tracks as seed
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/top/tracks?limit=5&time_range=short_term",
        headers=headers
    )
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get top tracks'}), 500
    
    top_tracks = response.json()
    seed_tracks = [track['id'] for track in top_tracks.get('items', [])[:5]]
    
    if not seed_tracks:
        return jsonify({'recommendations': []})
    
    # Get recommendations
    seed_str = ','.join(seed_tracks)
    response = requests.get(
        f"{SPOTIFY_API_BASE}/recommendations?seed_tracks={seed_str}&limit=20",
        headers=headers
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        recs = []
        
        for track in recommendations.get('tracks', []):
            recs.append({
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album'].get('images') else None,
                'uri': track['uri'],
                'preview_url': track.get('preview_url')
            })
        
        return jsonify({'recommendations': recs})
    
    return jsonify({'error': 'Failed to get recommendations'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)