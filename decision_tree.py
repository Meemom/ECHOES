"""CSC111 Project 2: Spotify Recommendation System - Decision Tree

This module provides the functions to create a decision tree that recommends songs based on an input song.
"""

from typing import Any, Optional
from dataclasses import dataclass
import operator
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


@dataclass
class Spotipy:
    """A class to interact with Spotify Web API for authentication and fetching song features.

    Instance Attributes:
        - client_id: the unique client identifier for authenticating with the Spotify API.
        - client_secret: the secret key used in conjunction with the client_id for API authentication.
        - sp: An instance of the `spotipy.Spotify` class, which is used to interact with the Spotify Web API.
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
        """Retrieves audio features for the given song."""
        results = self.sp.search(q=song_title, type='track', limit=1)  # finds the first track matching the song_title
        if not results['tracks']['items']:  # if the song does not exist
            return None  # Song not found

        track_id = results['tracks']['items'][0]['id']  # retrieve the song id
        features = self.sp.audio_features(track_id)[0]  # retrieves audio features for the song with the track_id

        return {
            'id': track_id,
            'energy': features['energy'],
            'danceability': features['danceability'],
            'acousticness': features['acousticness'],
            'tempo': features['tempo']
        }


@dataclass
class Node:
    """A class representing a node in the decision tree."""
    attribute: Optional[str]  # The audio feature used for splitting (e.g., 'energy', 'tempo')
    threshold: Optional[float]  # The threshold value for splitting (e.g., energy > 0.5)
    left: Optional['Node']  # Left branch (values below threshold)
    right: Optional['Node']  # Right branch (values above threshold)
    songs: Optional[list[str]]  # List of recommended songs (for leaf nodes)

    def __init__(self, attribute: Optional[str] = None, threshold: Optional[float] = None,
                 songs: Optional[list[str]] = None) -> None:
        """Initializes a Node with an optional splitting attribute and song list."""
        self.attribute = attribute
        self.threshold = threshold
        self.left = None
        self.right = None
        self.songs = songs if songs else []

    def is_leaf(self) -> bool:
        """Checks if the node is a leaf (i.e., contains song recommendations)."""
        return bool(self.songs) and self.attribute is None


@dataclass
class SongRecommendationTree:
    """A decision tree for recommending songs based on audio features."""
    sp: Spotipy
    root_song: str
    tree: Optional[Node]

    def __init__(self, sp: Spotipy, root_song: str) -> None:
        """Initializes a decision tree with the given root_song."""
        self.sp = sp
        self.root_song = root_song
        self.tree = self.build_tree(root_song)

    def build_tree(self, song_title: str) -> Optional[Node]:
        """Constructs a decision tree by splitting based on song features."""
        song_features = self.sp.get_song_features(song_title)
        if song_features is None:
            return None

        # Extract only numeric features for splitting
        features_to_split = [
            audio_feature for audio_feature, value in song_features.items()
            if isinstance(value, (int, float)) and feature not in ['id']
        ]

        root_node = Node(attribute=None, threshold=None, songs=[song_title])

        for feature in features_to_split:
            target_value = song_features[feature]
            recommended_songs = self.recommended_songs_by_feature(
                song_id=song_features['id'], feature=feature, target_value=target_value
            )

            if recommended_songs:
                left_node = Node(attribute=feature, threshold=target_value, songs=None)
                right_node = Node(attribute=feature, threshold=target_value, songs=None)

                root_node.left = left_node
                root_node.right = right_node

        return root_node

    def recommended_songs_by_feature(self, song_id: str, feature: str, target_value: float,
                                     limit: int = 10, comparison: str = 'closest') -> list[str]:
        """Returns similar songs to the given song based on a specific audio feature."""
        comparison_ops = {
            '>=': operator.ge,  # Greater than or equal to
            '<': operator.lt,   # Less than
        }

        recommendations = self.sp.recommendations(seed_tracks=[song_id], limit=limit)['tracks']

        recommended_songs = []
        for track in recommendations:
            track_id = track['id']
            feature_value = self.sp.get_song_features(track_id)[feature]

            if comparison == 'closest':
                if abs(feature_value - target_value) < 0.1:
                    recommended_songs.append(track['name'])
            elif comparison in comparison_ops:
                if comparison_ops[comparison](feature_value, target_value):
                    recommended_songs.append(track['name'])

        return recommended_songs

    def print_tree(self, node: Node, indent: str = "") -> None:
        """Recursively prints the structure of the decision tree."""
        if node is None:
            return

        if node.is_leaf():
            print(f"{indent}Leaf Node - Songs: {node.songs}")
        else:
            print(f"{indent}Node - Feature: {node.attribute}, Threshold: {node.threshold}")
            print(f"{indent}Left ->", end=" ")
            self.print_tree(node.left, indent + "  ")
            print(f"{indent}Right ->", end=" ")
            self.print_tree(node.right, indent + "  ")


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    CLIENT_ID = 'your_client_id'
    CLIENT_SECRET = 'your_client_secret'

    spotipy_instance = Spotipy(CLIENT_ID, CLIENT_SECRET)

    # start the simulation with a song
    song = 'ARE WE STILL FRIENDS?'  # example song
    recommendation_tree = SongRecommendationTree(spotipy_instance, song)

    # print the decision tree structure
    recommendation_tree.print_tree(recommendation_tree.tree)
