"""
Author: Julia Sinclair
Date: 2025-03-30
Desc: This file contains the code for the recommnder graph element of our project. Included in this
file is the _Vertex and Graph classes that we will be using in our main function.

- modify the song class from the Spotipy class in decision trees
"""
from __future__ import annotations
from spotipy import Spotify
import oauth_activation
import csv
from typing import Any, Optional

import networkx as nx


class _Vertex:
    """
    This class defines the vertex of the graph for the spotipy recommender
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any) -> None:
        """

        """
        self.item = item
        self.neighbours = set()


class _SongVertex(_Vertex):
    """
    This concrete class inherits from the general vertex class to create a vertex for the
    songs of the graph
    """
    artist: str

    def __init__(self, song_title: str, artist: str) -> None:
        """

        """
        super().__init__(song_title)
        self.neighbours = set()
        self.artist = artist


class Graph:
    """
    This graph maps songs to their _____

    """
    user_vertex_id: str
    _user_vertices: dict[Any, _Vertex]
    _song_vertices: dict[Any, _SongVertex]

    def __init__(self, current_user: str) -> None:
        """
        The initializer method for Graph
        """
        self.user_vertex_id = current_user
        self._song_vertices = {}
        self._user_vertices = {}

    def add_edge(self, username: str, song_title: str, artist: str) -> None:
        """
        This method creates an edge between the user with the specified username and song
        with the specified song_title.
        """
        song_id = "title:" + song_title + "artist:" + artist
        if username in self._user_vertices and song_id in self._song_vertices:
            user = self._user_vertices[username]
            song = self._song_vertices[song_id]

            user.neighbours.add(song)
            song.neighbours.add(user)
        else:
            raise ValueError

    def add_song_vertex(self, title: str, artist: str) -> None:
        """
        This method adds a song vertex to the graph
        """
        song_id = "title:" + title + "artist:" + artist
        if song_id not in self._song_vertices:
            self._song_vertices[song_id] = _SongVertex(title, artist)

    def add_user_vertex(self, item: Any, main_user: bool) -> None:
        """
        This method adds a user vertex to the graph
        """
        if item not in self._user_vertices:
            self._user_vertices[item] = _Vertex(item)

        if main_user:
            self.user_vertex_id = item

    def _get_similar_users(self) -> list[str]:
        """
        This method returns a list of the usernames for the five most similar users to the current_user
        """

    def _get_song_recs(self, similar_users: list[str]) -> list[list[str]]:
        """
        This method returns a list of three song ids per similar user which
        are not currently in the user's currently saved songs (neighbours)
        """

    def get_recommendations(self, seen: set) -> list[list[tuple]]:
        """
        This method returns recommendations to the user based on their listened to songs.
        The method returns a tuple of two string: one is the song title, the other is the song url.
        Three nested lists of tuples -- going from most simiular songs

        example return formatting for GUI:
        SONG RECOMMENDATONS:
        Most similar:
        - song
        - song
        - song

        Second most similar:
        - song
        - song
        - song

        Third most similar:
        - song
        - song
        - song
        """

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note that this method is provided for you, and you shouldn't change it.
        """
        graph_nx = nx.Graph()
        all_vertices = self._song_vertices | self._user_vertices
        for v in all_vertices.values():
            if isinstance(v, _SongVertex):
                node_type = 'book'
            else:
                node_type = 'review'

            graph_nx.add_node(v.item, kind=node_type)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    if isinstance(u, _SongVertex):
                        node_type = 'book'
                    else:
                        node_type = 'review'
                    graph_nx.add_node(u.item, kind=node_type)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx


def _load_curr_user_songs(spotify_info: Spotify, graph: Graph) -> None:
    """
    Loads the current user's songs into the graph
    """
    curr_user_tracks = spotify_info.current_user_saved_tracks(limit=100)
    graph.add_user_vertex("current_user", True)
    for track_info in curr_user_tracks['items']:
        title = track_info['track']['name']
        artist = track_info['track']['album']['artists'][0]['name']

        graph.add_song_vertex(title, artist)
        graph.add_edge("current_user", title, artist)


def load_song_listening_graph(listening_info_file: str, spotify_info: Spotify) -> Graph:
    """
    This method creates a graph based on the kaggle data set and the current user's information
    """
    graph_so_far = Graph("current_user")
    users_so_far = set()

    # load songs and associated listeners
    with open(listening_info_file, 'r', newline='', encoding='utf-8') as file:

        reader = csv.reader(file)

        # get past the headers
        next(reader)
        limit = 0

        # add each song to the graph
        for row in reader:
            # limit for testing purposes
            if limit == 500000:
                break

            graph_so_far.add_song_vertex(row[2], row[1])

            if row[0] not in users_so_far:
                graph_so_far.add_user_vertex(row[0], False)
                users_so_far.add(row[0])

            graph_so_far.add_edge(row[0], row[2], row[1])
            limit += 1

    _load_curr_user_songs(spotify_info, graph_so_far)

    # final return statement
    return graph_so_far


if __name__ == '__main__':
    CLIENT_ID = "6491f8aa9e064c7d9c74d3666dcfabdd"
    CLIENT_SECRET = "b9b859e1b50144baa17d7277cdb0708e"
    REDIRECT_URI = "http://localhost:8888/callback"
    SCOPE = "user-library-read"
    CACHE_PATH = ".spotify_cache"

    auth = oauth_activation.SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
    auth.setup_auth_manager()
    spot_test = auth.authenticate()

    my_graph = load_song_listening_graph('spotify_dataset.csv', spot_test)
