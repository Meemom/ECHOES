"""
CSC111 Project 2: Spotify Recommendation System - Oauth Activation Module
This module handles the Spotify OAuth authentication process and provides endpoints for user data retrieval and song recommendations.
"""
import python_ta
import os
from flask import Flask, session, url_for, redirect, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional, Dict, Any

# constants TODO: make sure to unify the client_id, client_secret, and redirect uri across all files
CLIENT_ID = "f8f5475f76b6492d865574179fb39c3b"
CLIENT_SECRET = "a6eb99e6534d4625ab7f78cef37f091b"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "user-library-read user-top-read playlist-read-private"
CACHE_PATH = ".spotify_cache"
app = Flask(__name__)
app.secret_key = os.urandom(64)

class SpotifyAuthentication:
    """
    Handles Spotify authentication using Flask session for caching tokens.
    
    Instance Attributes:
    - client_id: The Spotify client ID.
    - client_secret: The Spotify client secret.
    - redirect_uri: The redirect URI for the application.
    - scope: The scope of access requested from the user.
    - auth_manager: The SpotifyOAuth manager instance.
    - spotify: The Spotify client instance.
    """
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str) -> None:
        """Initializes the SpotifyAuthentication class with API credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_manager = None
        self.spotify = None

    def setup_auth_manager(self) -> None:
        """Sets up the SpotifyOAuth manager with Flask session cache handler."""
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=CACHE_PATH,
            show_dialog=True
        )

    def authenticate(self) -> Optional[Spotify]:
        """Authenticates the user and returns a Spotify client instance."""
        try:
            if self.auth_manager is None:
                self.setup_auth_manager()

            self.spotify = Spotify(auth_manager=self.auth_manager)

            # test connectedness
            current_user = self.spotify.current_user()
            print(f"Successfully authenticated as: {current_user['display_name']}")

            return self.spotify

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return None

    def get_auth_url(self) -> str:
        """Returns the authorization URL for the user to log in."""
        if self.auth_manager is None:
            self.setup_auth_manager()

        return self.auth_manager.get_authorize_url()

    def get_token(self, code: str) -> Dict[str, Any]:
        """Exchange the authorization code for an access token."""
        if self.auth_manager is None:
            self.setup_auth_manager()

        return self.auth_manager.get_access_token(code)
    
    def validate_token(self) -> bool:
        """Check if the current token is valid."""
        if self.auth_manager is None:
            return False

        token_info = self.auth_manager.get_cached_token()

        if token_info:
            return not self.auth_manager.is_token_expired(token_info)

        return False
    
    def refresh_token(self) -> Optional[Spotify]:
        """Refresh the access token and update session."""
        if self.auth_manager is None:
            return None
        
        token_info = self.auth_manager.get_cached_token()

        if token_info:
            new_token = self.auth_manager.refresh_access_token(token_info['refresh_token'])
            session["token_info"] = new_token  # saves new token in session
            self.spotify = Spotify(auth_manager=self.auth_manager)
            return self.spotify

        return None


@app.route("/")
def home():
    """Home page route that redirects to authentication if needed."""
    authenticator = SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
    authenticator.setup_auth_manager()
    
    if not authenticator.validate_token():
        auth_url = authenticator.get_auth_url()
        return redirect(auth_url)

    return redirect(url_for("success"))


@app.route("/callback")
def callback():
    """Callback route for Spotify authentication."""
    try:
        authenticator = SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
        authenticator.setup_auth_manager()
        
        # Make sure code parameter exists
        if "code" not in request.args:
            return "Error: No authorization code provided. Please try again.", 400
            
        authenticator.get_token(request.args["code"])
        return redirect(url_for("success"))
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return f"Error during authentication: {str(e)}", 500


@app.route("/success")
def success():
    """User data route that retrieves and displays user information."""
    try:
        authenticator = SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
        authenticator.setup_auth_manager()
        
        if not authenticator.validate_token():
            auth_url = authenticator.get_auth_url()
            return redirect(auth_url)
        
        # return a simple HTML page informing the user they can return to the app
        return """
        <!DOCTYPE html>
        <html>
        <body>

        <h1 style="font-family:verdana">Authentification Successful!</h1>

        <p style="font-family:verdana">You may now close the window.</p>
        <p style="font-family:verdana">Hope you get some awesome song recs!</p>

        </body>
        </html>
        """
        
    except Exception as e:
        print(f"Success route error: {str(e)}")
        return f"Error displaying success page: {str(e)}", 500

@app.route("/logout")
def logout():
    """Logout route that clears the session and redirects to home."""
    session.clear()
    return redirect(url_for("home"))


if __name__ == '__main__':  # run the app
    app.run(debug=True)
    python_ta.check_all(config={
    'extra-imports': ["typing", "spotipy", "spotipy.oauth2", "os", "flask"],
    'max-line-length': 120
})
