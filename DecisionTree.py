import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Any, Optional

class Spotipy:
    """A class to interact with Spotify Web API for authentication and fetching song features.

    Instance Attributes:
        - client_id: Spotify API client ID.
        - client_secret: Spotify API client secret.
        - sp: An instance of the Spotipy client for making API requests.
    """
    client_id: str
    client_secret: str
    sp: spotipy.Spotify

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initializes the Spotipy class with authentication credentials."""
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        )

    def get_song_features(self, song_title: str) -> Optional[dict[str, Any]]:
        """Retrieves audio features for the given song.

        Returns:
            - A dictionary containing song features if found, otherwise None.
        """
        results = self.sp.search(q=song_title, type='track', limit=1)
        if not results['tracks']['items']:
            return None  # Song not found

        track_id = results['tracks']['items'][0]['id']
        features = self.sp.audio_features(track_id)[0]

        return {
            'id': track_id,
            'energy': features['energy'],
            'danceability': features['danceability'],
            'acousticness': features['acousticness'],
            'tempo': features['tempo'],
            'genre': features.get('genre', 'Unknown'),  # Handle missing genre
        }

class Node:
    """A class representing a node in the decision tree.

    Instance Attributes:
        - attribute: The audio feature used for splitting.
        - threshold: The threshold value for splitting.
        - left: The left branch (values below threshold).
        - right: The right branch (values above threshold).
        - songs: List of recommended songs (for leaf nodes).
    """
    attribute: Optional[str]
    threshold: Optional[float]
    left: Optional['Node']
    right: Optional['Node']
    songs: list[str]

    def __init__(self, attribute: Optional[str] = None, threshold: Optional[float] = None, songs: Optional[list[str]] = None) -> None:
        """Initializes a Node with an optional splitting attribute and song list."""
        self.attribute = attribute
        self.threshold = threshold
        self.left = None
        self.right = None
        self.songs = songs if songs else []

    def is_leaf(self) -> bool:
        """Checks if the node is a leaf (i.e., contains song recommendations)."""
        return bool(self.songs) and self.attribute is None

class SongRecommendationTree:
    """A decision tree for recommending songs based on audio features.

    Instance Attributes:
        - sp: An instance of Spotipy.
        - root_song: The starting song for recommendations.
        - tree: The decision tree created based on the given root_song.
    """
    sp: Spotipy
    root_song: str
    tree: Optional[Node]

    def __init__(self, sp: Spotipy, root_song: str) -> None:
        """Initializes a decision tree with the given root_song."""
        self.sp = sp
        self.root_song = root_song
        self.tree = None  # The tree will be built later
