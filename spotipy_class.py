"""
Description
"""
from typing import Any, Optional
# import operator
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotipyExtended(spotipy.Spotify):
    """A class to interact with Spotify Web API for authentication and fetching song features.

    Instance Attributes:
        - client_id:
        - client_secret:
    """
    client_id: str
    client_secret: str

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initializes the Spotipy class with the client credentials manager."""

        # Set up the credentials manager to handle token fetching automatically
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )

        # Initialize Spotipy with the credentials manager
        super().__init__(client_credentials_manager=client_credentials_manager)

    def get_song_features(self, song_title: str) -> Optional[dict[str, Any]]:
        """Retrieves audio features for the given song."""
        results = self.search(q=song_title, type='track', limit=1)  # Uses self instead of self.sp
        if not results['tracks']['items']:  # If no song is found
            return None

        track_id = results['tracks']['items'][0]['id']  # Retrieve the song ID
        features = self.audio_features(track_id)[0]  # Fetch audio features

        return {
            'id': track_id,
            'energy': features['energy'],
            'danceability': features['danceability'],
            'acousticness': features['acousticness'],
            'tempo': features['tempo']
        }

    def get_song_identifiers(self, song_title: str, artist: str) -> Optional[tuple]:
        """
        This method searches for the Spotify song's id and url and returns both as a tuple.
        If the song can't be found, the function returns None. Returns a tuple
        """
        results = self.search(q='track:' + song_title + ' artist:' + artist, type='track', limit=10)

        # this is an empty list if the song can't be found
        if not results['tracks']['items']:
            return None

        track_id = results['tracks']['items'][0]['id']
        track_url = results['tracks']['items'][0]['external_urls']['spotify']

        return track_id, track_url
