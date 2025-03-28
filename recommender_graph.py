"""
Author: Julia Sinclair
Date: 2025-03-28
Desc: This file contains the code for the recommnder graph element of our project. Included in this
file is the _Vertex and Graph classes that we will be using in our main function.

- modify the song class from the Spotipy class in decision trees
"""
from __future__ import annotations
from spotipy_class import SpotipyExtended
import csv
from typing import Any, Optional
import pandas

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
    url: Optional[str]
    song_id: Optional[str]

    def __init__(self, song_title: str, song_id: str, url: str) -> None:
        """

        """
        super().__init__(song_title)
        self.neighbours = set()
        self.url, self.song_id = url, song_id

    def add_neighbours(self, user_id) -> None:
        """
        This method adds neighbours to the _Song_Vertex
        """


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

    def add_edge(self, username: str, song_title: str) -> None:
        """
        This method creates an edge between the user with the specified username and song
        with the specified song_title.
        """
        if username in self._user_vertices and song_title in self._song_vertices:
            user = self._user_vertices[username]
            song = self._song_vertices[song_title]

            user.neighbours.add(song)
            song.neighbours.add(user)
        else:
            raise ValueError

    def add_song_vertex(self, title: str, song_id: str, url: str) -> None:
        """
        This method adds a song vertex to the graph
        """
        if title not in self._song_vertices:
            self._song_vertices[title] = _SongVertex(title, song_id, url)

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
        This method returns a list of the usernames for the three most similar users to the current_user
        """

    def _get_song_recs(self, similar_users: list[str]) -> list[list[str]]:
        """
        This method returns a list of three song ids per similar user which
        are not currently in the user's currently saved songs (neighbours)
        """

    def get_recommendations(self) -> list[list[tuple]]:
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


def _load_song(song_title: str, artist_name: str, spotify_info: SpotipyExtended, graph: Graph, seen: set) -> bool:
    """
    This

    Return True if the song exists and is added, False otherwise.
    """
    song_info = spotify_info.get_song_identifiers(song_title, artist_name)

    if song_info is not None and song_info[0] not in seen:
        graph.add_song_vertex(song_title, song_info[0], song_info[1])
        seen.add(song_info[0])
        return True

    return False


def _load_curr_user_songs(spotify_info: SpotipyExtended, graph: Graph) -> None:
    """
    TODO - implement this function (need to get around ouath errors with spotipy)
    """
    curr_user_tracks = spotify_info.current_user_saved_tracks()
    for idx, item in enumerate(curr_user_tracks['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])


def load_song_listening_graph(listening_info_file: str, spotify_info: SpotipyExtended) -> Graph:
    """
    This method creates a graph based on the kaggle data set and the current user's information

    CURRENT ERROR:
    UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 2511: character maps to <undefined>
    - USE PANDAS to SAMPLE data set (because 1 million songs is TOO MANY SONGS)
    """
    graph_so_far = Graph("current_user")
    users_so_far = set()
    songs_so_far = set()

    # load songs and associated listeners
    with open(listening_info_file, 'r', newline='', encoding='utf-8') as file:

        reader = csv.reader(file)

        # get past the headers
        next(reader)

        # add each song to the graph
        for row in reader:
            result = _load_song(row[2], row[1], spotify_info, graph_so_far, songs_so_far)

            if not result:
                continue

            if row[0] not in users_so_far:
                graph_so_far.add_user_vertex(row[0], False)
                users_so_far.add(row[0])

            # this is for debugging purposes
            print("Values: " + row[0] + ", " + row[2])

            graph_so_far.add_edge(row[0], row[2])

    # TODO - load the songs for current user
    # _load_curr_user_songs(spotify_info, graph_so_far)

    # final return statement
    return graph_so_far
