# forked from albumcovers/spotify

import os
from flask import Flask, render_template, jsonify, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask_cors import CORS
from spotipy.cache_handler import MemoryCacheHandler, CacheHandler

class CustomCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None
    def save_token_to_cache(self, token_info):
        pass

# load configuration from environment for security
USERNAME = os.getenv('SPOTIFY_USERNAME')
SCOPE = 'user-read-currently-playing'
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')  # could  be anything
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REFRESH_TOKEN  = os.getenv('SPOTIFY_REFRESH_TOKEN')   



app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_access_token():
    """
    exchange stored REFRESH_TOKEN for a fresh access token.
    returns the access token string, or None on failure.
    """
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, REDIRECT_URI]):
        # missing config
        return None

    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=False,
        cache_handler=CustomCacheHandler()
    )
    # use refresh token to get new access token
    token_info = oauth.refresh_access_token(REFRESH_TOKEN)
    return token_info.get('access_token')

def fetch_currently_playing():
    """
    fetch user a’s currently playing item with fresh token.
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

    # ensure item exists
    if not playing or not playing.get('item'):
        return None
    return playing['item']

@app.route('/')
def index():
    """
    main page: shows user a’s current track.
    anyone visiting sees the same info.
    """
    item = fetch_currently_playing()
    if not item:
        # nothing playing or error: show placeholder
        return render_template(
            'index.html',
            title='nothing playing',
            artist='no one',
            final_image_url='https://i.pinimg.com/564x/46/46/dd/4646dd0ebb3f008253e4deea38d233de--emoji-emoticons-emojis.jpg'
        )

    # extract details
    artist    = item['artists'][0]['name']
    track     = item['name']
    image_url = item['album']['images'][0]['url']
    
    return render_template(
        'index.html',
        title=track,
        artist=artist,
        final_image_url=image_url
    )

# helper factory for simple API endpoints
def make_simple_api(field_path):
    """
    returns a view that drills into item via field_path.
    field_path: e.g. ['artists',0,'name'] or ['album','images',0,'url']
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
    """
    handle unexpected errors.
    for API: return simple defaults.
    for page: show placeholder.
    """
    ep = request.endpoint
    if ep == 'api_title':
        return 'nothing', 200
    if ep == 'api_artist':
        return 'no one', 200
    if ep == 'api_image':
        return jsonify(error='no image'), 200
    # fallback for '/'
    return render_template(
        'index.html',
        title='nothing',
        artist='no one',
        final_image_url='https://i.pinimg.com/564x/46/46/dd/4646dd0ebb3f008253e4deea38d233de--emoji-emoticons-emojis.jpg'
    ), 200

@app.errorhandler(404)
def not_found(error):
    """
    redirect unknown routes back to index.
    """
    return redirect('/'), 302

if __name__ == '__main__':
    # local dev: run on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
