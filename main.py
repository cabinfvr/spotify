# forked from albumcovers/spotify

import os
from flask import Flask, render_template, jsonify, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler

class CustomCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None
    def save_token_to_cache(self, token_info):
        pass

# load configuration from environment for security
USERNAME       = os.getenv('SPOTIFY_USERNAME')
SCOPE          = 'user-read-currently-playing'
REDIRECT_URI   = os.getenv('SPOTIFY_REDIRECT_URI')  
CLIENT_ID      = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET  = os.getenv('SPOTIFY_CLIENT_SECRET')
REFRESH_TOKEN  = os.getenv('SPOTIFY_REFRESH_TOKEN')   

app = Flask(__name__)

# add cors headers after every request for /api/*
@app.after_request
def add_cors_headers(response):
    if request.path.startswith('/api/'):
        response.headers['access-control-allow-origin']  = '*'
        response.headers['access-control-allow-methods'] = 'GET, OPTIONS'
        response.headers['access-control-allow-headers'] = 'Content-Type'
    return response

def get_access_token():
    """
    exchange stored REFRESH_TOKEN for a fresh access token.
    returns the access token string, or None on failure.
    """
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, REDIRECT_URI]):
        return None

    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=False,
        cache_handler=CustomCacheHandler()
    )
    token_info = oauth.refresh_access_token(REFRESH_TOKEN)
    return token_info.get('access_token')

def fetch_currently_playing():
    """
    fetch user’s currently playing item with fresh token.
    returns the JSON dict or None if nothing playing or error.
    """
    access_token = get_access_token()
    if not access_token:
        return None

    spotify = spotipy.Spotify(auth=access_token)
    try:
        playing = spotify.currently_playing()
    except Exception:
        return None

    if not playing or not playing.get('item'):
        return None
    return playing['item']

@app.route('/')
def index():
    """
    main page: shows user’s current track.
    anyone visiting sees the same info.
    """
    item = fetch_currently_playing()
    if not item:
        return render_template(
            'index.html',
            title='nothing playing',
            artist='no one',
            final_image_url='https://i.pinimg.com/564x/46/46/dd/4646dd0ebb3f008253e4deea38d233de--emoji-emoticons-emojis.jpg'
        )
    artist    = item['artists'][0]['name']
    track     = item['name']
    image_url = item['album']['images'][0]['url']
    return render_template(
        'index.html',
        title=track,
        artist=artist,
        final_image_url=image_url
    )

def make_simple_api(field_path):
    """
    returns a view that drills into item via field_path.
    """
    def view():
        item = fetch_currently_playing()
        if not item:
            return jsonify(error='nothing playing'), 204
        data = item
        for key in field_path:
            data = data[key]
        return data
    return view

# public API routes for title, artist, image
app.add_url_rule('/api/title',  'api_title',  make_simple_api(['name']),               methods=['GET'])
app.add_url_rule('/api/artist', 'api_artist', make_simple_api(['artists',0,'name']),    methods=['GET'])
app.add_url_rule('/api/image',  'api_image',  make_simple_api(['album','images',0,'url']), methods=['GET'])

@app.errorhandler(500)
def internal_error(error):
    ep = request.endpoint
    if ep == 'api_title':
        return 'nothing', 200
    if ep == 'api_artist':
        return 'no one', 200
    if ep == 'api_image':
        return jsonify(error='no image'), 200
    return render_template(
        'index.html',
        title='nothing',
        artist='no one',
        final_image_url='https://i.pinimg.com/564x/46/46/dd/4646dd0ebb3f008253e4deea38d233de--emoji-emoticons-emojis.jpg'
    ), 200

@app.errorhandler(404)
def not_found(error):
    return redirect('/'), 302

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
