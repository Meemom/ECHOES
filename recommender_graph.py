"""
Author: Julia Sinclair
Date: 2025-03-30
Desc: This file contains the code for the recommnder graph element of our project. Included in this
file is the _Vertex and Graph classes that we will be using in our main function.

"""
from __future__ import annotations
import csv
from typing import Any, Optional

from spotipy import Spotify
import pandas as pd

import oauth_activation


class _Vertex:
    """
    This class defines the vertex of the graph for the spotipy recommender
    """
    item: Any
    neighbours: set[_SongVertex]

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
    neighbours: set[_Vertex]

    def __init__(self, song_title: str, artist: str) -> None:
        """

        """
        super().__init__(song_title)
        self.neighbours = set()
        self.artist = artist


class Graph:
    """
    This graph maps songs to their _____

    Preconditions:
        -
    """
    user_vertex_id: Optional[str]
    _user_vertices: dict[Any, _Vertex]
    _song_vertices: dict[Any, _SongVertex]
    spotify_info: Optional[Spotify]

    def __init__(self, spotify_info: Optional[Spotify] = None) -> None:
        """
        The initializer method for Graph
        """
        self.user_vertex_id = None
        self._song_vertices = {}
        self._user_vertices = {}
        self.spotify_info = spotify_info

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

    def _get_connected_users(self) -> dict[Any, list[int]]:
        """
        This method gets all connected users who are connected with one song in between them.

        >>> graph = Graph()
        >>> graph.add_user_vertex("user_1", True)
        >>> graph.add_user_vertex("user_2", False)
        >>> graph.add_user_vertex("user_3", False)
        >>> graph.add_song_vertex("Let Down", "Radiohead")
        >>> graph.add_song_vertex("Kiss of Life", "Sade")
        >>> graph.add_song_vertex("Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Let Down", "Radiohead")
        >>> graph.add_edge("user_2", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_2", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_3", "Let Down", "Radiohead")
        >>> graph._get_connected_users() == {"user_2": [1, 2], "user_3": [2, 3]}
        True
        """
        user_vertex = self._user_vertices[self.user_vertex_id]
        connected_so_far = {}

        for song in user_vertex.neighbours:
            # removes the main user vertex from a copy of the song neighbours so that
            # the main user is not included in the final dictionary (we can't give recommendations from
            # someone's own library)
            connected_users = song.neighbours.copy()
            connected_users.remove(user_vertex)

            for connected_user in connected_users:
                if connected_user.item in connected_so_far:
                    connected_so_far[connected_user.item][0] += 1
                else:
                    connected_so_far[connected_user.item] = [1, len(connected_user.neighbours)]

        return connected_so_far

    def _get_most_similar_user(self) -> str:
        """
        This method returns a username for a user with the highest similarity scores to the current_user
        - need to ensure that len(neighbours) is not the same as number of connections

        Returns the current user vertex id if there are NO CONNECTED USERS

        >>> graph = Graph()
        >>> graph.add_user_vertex("user_1", True)
        >>> graph.add_user_vertex("user_2", False)
        >>> graph.add_user_vertex("user_3", False)
        >>> graph.add_song_vertex("Let Down", "Radiohead")
        >>> graph.add_song_vertex("Kiss of Life", "Sade")
        >>> graph.add_song_vertex("Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Let Down", "Radiohead")
        >>> graph.add_edge("user_2", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_2", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_3", "Let Down", "Radiohead")
        >>> graph._get_most_similar_user()
        'user_3'
        >>> graph_2 = Graph()
        >>> graph_2.add_user_vertex("user_1", True)
        >>> graph_2.add_user_vertex("user_2", False)
        >>> graph_2._get_most_similar_user()
        'user_1'
        """
        connected_users = self._get_connected_users()
        most_similar_user = self.user_vertex_id
        max_score_so_far = 0

        for user_id in connected_users:
            # if the number of connections is the same as the number of neighbours of the current user's id
            # then there are no new recommendations to be
            if (len(self._user_vertices[self.user_vertex_id].neighbours)
                    == len(self._user_vertices[user_id].neighbours)
                    and len(self._user_vertices[self.user_vertex_id].neighbours)
                    == connected_users[user_id][0]):
                continue
            else:
                similarity_score = connected_users[user_id][0] / connected_users[user_id][1]
                if similarity_score > max_score_so_far:
                    most_similar_user = user_id
                    max_score_so_far = similarity_score

        return most_similar_user

    def _get_song_recs(self, similar_user: str) -> list[list[str]]:
        """
        This method returns a set of three song ids per similar user which
        are not currently in the user's currently saved songs (neighbours)
        - This includes URL for the songs

        If a URL for the song cannot be found at recommendation i, then the lst[i][1] == ''

        TODO - preconditions
        Preconditions:
            - similar_user in self._user_vertices
            - similar_user != self.user_vertex_id

        >>> graph = Graph()
        >>> graph.add_user_vertex("user_1", True)
        >>> graph.add_user_vertex("user_3", False)
        >>> graph.add_song_vertex("Let Down", "Radiohead")
        >>> graph.add_song_vertex("Kiss of Life", "Sade")
        >>> graph.add_song_vertex("Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Let Down", "Radiohead")
        >>> graph.add_edge("user_3", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_3", "Let Down", "Radiohead")
        >>> graph._get_song_recs("user_3")
        [['Kiss of Life by Sade', '']]
        """
        lst_so_far = []
        for song in self._user_vertices[similar_user].neighbours:
            sublist = []
            if song not in self._user_vertices[self.user_vertex_id].neighbours:
                sublist.append(song.item + " by " + song.artist)

                if self.spotify_info is not None:
                    results = self.spotify_info.search(q='track:' + song.item + ' artist:' + song.artist,
                                                       type='track', limit=1)
                    # checks to see if we get back a value
                    if results['tracks']['items']:
                        # gets the URL to the
                        sublist.append(results['tracks']['items'][0]['external_urls']['spotify'])
                else:
                    sublist.append('')

                lst_so_far.append(sublist)

        return lst_so_far

    def get_recommendations(self, limit: int = 3) -> list[list[str]]:
        """
        This method returns recommendations to the user based on their listened to songs.
        The method returns a list of tuples of two string: one is the song title, the other is the song url.
        Three nested lists of tuples -- going from most simiular songs

        Returns an empty list if there are no similar users

        TODO - doctests
        TODO - preconditions

        Preconditions:
            - limit >= 0

        example return formatting for GUI:
        SONG RECOMMENDATONS:
        You may like:
        - song
        - song
        - song
        """
        similar_user = self._get_most_similar_user()
        if similar_user == self.user_vertex_id:
            return []

        recommendation_results = self._get_song_recs(similar_user)
        return recommendation_results[0:limit]


def _load_curr_user_songs(spotify_info: Spotify, graph: Graph) -> bool:
    """
    Loads the current user's songs into the graph
    """
    curr_user_tracks = spotify_info.current_user_saved_tracks(limit=50)

    if curr_user_tracks is None:
        return False

    graph.add_user_vertex("current_user", True)
    for track_info in curr_user_tracks['items']['track']:
        title = track_info['name']
        artist = track_info['album']['artists'][0]['name']

        graph.add_song_vertex(title, artist)
        graph.add_edge("current_user", title, artist)

    return True


def _load_hardcoded_user_songs(graph: Graph) -> None:
    """
    Loads the hardcoded versions of songs because I'm getting rate limited
    """
    graph.add_user_vertex("current_user", True)

    with open("data_user.csv", 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            graph.add_song_vertex(row[0], row[1])
            graph.add_edge("current_user", row[0], row[1])


def load_song_listening_graph(listening_info_file: str, spotify_info: Optional[Spotify]) -> Graph:
    """
    This method creates a graph based on the kaggle data set and the current user's information

    TODO - pandas sampling
    """
    graph_so_far = Graph(spotify_info)
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

    # _load_hardcoded_user_songs(graph_so_far) if the spot_test is not working -- DEMO WITHOUT OAUTH
    if spotify_info is None:
        _load_hardcoded_user_songs(graph_so_far)
    else:
        _load_curr_user_songs(spotify_info, graph_so_far)

    # final return statement
    return graph_so_far


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    CLIENT_ID = "d4438951382c4c05bceb265fd8de11ec"
    CLIENT_SECRET = "f6890c57cc42499581c685cd79dadded"
    REDIRECT_URI = "http://localhost:8888/callback"
    SCOPE = "user-library-read"
    CACHE_PATH = ".spotify_cache"

    # try:
    # auth = oauth_activation.SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
    # auth.setup_auth_manager()
    # spot_test = auth.authenticate()
    # except ():
    spot_test = None

    my_graph = load_song_listening_graph('spotify_dataset.csv', spot_test)

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ["spotipy", "oauth_activation", "__future__", "csv", "typing",
                          "pandas", "networkx"],
        'allowed-io': ["load_song_listening_graph", "_load_hardcoded_user_songs"],
        'max-line-length': 120,
        'max-nested-blocks': 4
    })
