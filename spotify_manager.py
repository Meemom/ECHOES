"""
CSC111 Project 2: Spotify Recommendation System - Spotify Manager Module
This module handles the Spotify authentication and API requests for the recommendation system.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from oauth_activation import Flask

# constants TODO: make sure to unify the client_id, client_secret, and redirect uri across all files
client_id = "f8f5475f76b6492d865574179fb39c3b"
client_secret = "a6eb99e6534d4625ab7f78cef37f091b"
redirect_uri = "http://localhost:5000/callback"

class SpotifyManager:
    """
    Manager class that automates handling Spotify authentication and API requests.
    """
    client_id: str
    client_secret: str
    redirect_uri: str

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope='user-library-read playlist-modify-private'  # TODO: subject to change, discuss w/ others first
        )
