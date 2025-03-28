"""CSC111 Project 2: Spotify Recommendation System - Decision Tree

This module provides the functions to create a decision tree that recommends songs based on an input song.
"""

from typing import Any, Optional
import pandas as pd
import kagglehub
import os
import operator
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# loading the dataset
dataset_path = ('/Users/jemimasilaen/.cache/kagglehub/datasets/bwandowando/spotify'
                '-songs-with-attributes-and-lyrics/versions/19/songs_with_attributes_and_lyrics.csv')
df = pd.read_csv(dataset_path)

class SpotipyExtended(spotipy.Spotify):
    """A class to interact with Spotify Web API for authentication and fetching song features."""
    dataset: pd.DataFrame

    def __init__(self, dataset: pd.DataFrame) -> None:
        """Initializes with the preloaded dataset."""
        # Initialize the parent (Spotipy) class with the provided auth_manager
        super().__init__(auth_manager=auth_manager)
        self.dataset = dataset

    def get_song_features(self, song_title: str) -> Optional[dict[str, Any]]:
        """Retrieves audio features for the given song from the Kaggle dataset."""
        # find the row in the dataset that matches the given song title
        song_data = self.dataset[self.dataset['name'].str.lower() == song_title.lower()]
        if song_data.empty:
            return None

        song = song_data.iloc[0] # selects the first row from song_data
        features = {
            'id': song['id'],
            'danceability': song['danceability'],
            'energy': song['energy'],
            'acousticness': song['acousticness'],
            'tempo': song['tempo'],
            'speechiness': song['speechiness']
        }

        return features


class Node:
    """A class representing a node in the decision tree."""
    attribute: Optional[str]  # The audio feature used for splitting (e.g., 'energy', 'tempo')
    threshold: Optional[float]  # The threshold value for splitting (e.g., energy > 0.5)
    left: Optional['Node']  # Left branch (values below threshold)
    right: Optional['Node']  # Right branch (values above threshold)
    songs: Optional[list[str]]

    def __init__(self, attribute: Optional[str] = None, threshold: Optional[float] = None,
                 songs: Optional[list[str]] = None) -> None:
        self.attribute = attribute
        self.threshold = threshold
        self.left = None
        self.right = None
        self.songs = songs if songs else []

    def is_leaf(self) -> bool:
        """Checks if the node is a leaf (i.e., contains song recommendations)."""
        return bool(self.songs) and self.attribute is None


class SongRecommendationTree:
    """A decision tree for recommending songs based on audio features."""
    sp: SpotipyExtended
    root_song: str
    tree: Optional[Node]

    def __init__(self, sp: SpotipyExtended, root_song: str) -> None:
        self.sp = sp
        self.root_song = root_song
        self.tree = self.build_tree(root_song)

    def build_tree(self, song_title: str) -> Optional[Node]:
        """Constructs a decision tree by splitting based on song features."""
        song_features = self.sp.get_song_features(song_title)
        if song_features is None:
            print("The given song is not found.")
            return None

        features_to_split = [
            audio_feature for audio_feature, value in song_features.items()
            if isinstance(value, (int, float)) and audio_feature != 'id'
        ]

        root_node = Node(attribute=None, threshold=None, songs=[song_title])

        for feature in features_to_split:
            target_value = song_features[feature]
            left_songs = self.recommended_songs_by_feature(
                song_id=song_features['id'], feature=feature, target_value=target_value, comparison='<'
            )
            right_songs = self.recommended_songs_by_feature(
                song_id=song_features['id'], feature=feature, target_value=target_value, comparison='>='
            )

            if left_songs and right_songs:
                left_node = Node(attribute=feature, threshold=target_value, songs=left_songs)
                right_node = Node(attribute=feature, threshold=target_value, songs=right_songs)

                root_node.left = left_node
                root_node.right = right_node

        return root_node

    def recommended_songs_by_feature(self, song_id: str, feature: str, target_value: float,
                                     limit: int = 10, comparison: str = 'closest') -> list[str]:
        comparison_ops = {
            '>=': operator.ge,
            '<': operator.lt,
        }

        # Fetch the recommendations once and process the songs
        recommendations = self.sp.recommendations(seed_tracks=[song_id], limit=limit)['tracks']

        recommended_songs = []

        # Store song features in a dictionary to avoid repeated API calls
        song_features_cache = {}

        for track in recommendations:
            track_id = track['id']
            # Check if we have the features cached already
            if track_id not in song_features_cache:
                feature_value = self.sp.get_song_features(
                    track['name'])  # Using track name here, or use track_id if available
                if feature_value and feature in feature_value:
                    song_features_cache[track_id] = feature_value[feature]
                else:
                    song_features_cache[track_id] = None

            feature_value = song_features_cache[track_id]
            if feature_value is None:
                continue  # Skip if no valid feature found

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
    CLIENT_ID = '673544b65c924a6e9dfb24c2b2624c6e'
    CLIENT_SECRET = '1812e2325a42479ab070a9bedfdcced9'
    REDIRECT_URI = 'http://localhost:8888/callback'
    SCOPE = 'user-library-read playlist-read-private user-top-read'

    # Step 1: Create SpotifyOAuth instance for authentication
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=SCOPE)

    # Step 2: Use auth_manager to authenticate and create a Spotipy client
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Step 3: Initialize SpotipyExtended with the authenticated Spotipy instance and dataset
    sp_extended = SpotipyExtended(dataset=df)

    song = 'ARE WE STILL FRIENDS?'  # Example song
    recommendation_tree = SongRecommendationTree(sp_extended, song)

    # Step 4: Print the decision tree structure
    recommendation_tree.print_tree(recommendation_tree.tree)
