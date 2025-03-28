import os

from flask import Flask, session, url_for, redirect, request, jsonify
from decision_tree import MISSING
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

client_id = "f8f5475f76b6492d865574179fb39c3b"
client_secret = "a6eb99e6534d4625ab7f78cef37f091b"
redirect_uri = "http://localhost:5000/callback"
scope = "user-library-read,user-top-read,playlist-read-private"

cache_handler = FlaskSessionCacheHandler(session)

sp_auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_auth)

@app.route("/")  # home page
def home():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_auth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for("userdata"))


@app.route("/callback")
def callback():  # Used so that the user doesn't have to login over and over again (unless we change scope)
    sp_auth.get_access_token(request.args["code"])
    return redirect(url_for("userdata"))


@app.route("/userdata")  # for the sake of testing out features, need to fix this up so we can make it to a useful page (perhaps profile data recap, just basic info)
def userdata():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp.auth.get_authorize_url()
        return redirect(auth_url)

    user = sp.current_user()
    top_tracks = sp.current_user_top_tracks(limit=10)["items"]

    return jsonify({
        "display_name": user["display_name"],
        "top_tracks": [{"name": t["name"], "popularity": t["popularity"]} for t in top_tracks]
    })


@app.route("/getplaylists")  # for the sake of testing out features
def get_playlists():
    if not sp_auth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp.auth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    playlist_info = [(playlist["name"], playlist["id"]) for playlist in playlists["items"]]
    playlists_html = "<br>".join([f"{name}: {url}" for name, url in playlist_info])

    return playlists_html


@app.route("/recommend", methods=["POST"])
def recommend():  # discuss with mima what command to use for "getting recs"
    data = request.json
    song_name = data.get("song")

    if not song_name:
        return jsonify({"error": "No song provided"}), 400

    recommendations = MISSING(song_name)  # TODO: fix after discussion
    return jsonify({"recommendations": recommendations})


@app.route("/logout")  # logout page
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)