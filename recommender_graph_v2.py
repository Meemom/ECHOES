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

    def __init__(self) -> None:
        """
        The initializer method for Graph
        """
        self.user_vertex_id = None
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

    def _get_connected_users(self) -> dict[Any, int]:
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
        >>> graph._get_connected_users() == {"user_2": 1, "user_3": 2}
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
                    connected_so_far[connected_user.item] += 1
                else:
                    connected_so_far[connected_user.item] = 1

        return connected_so_far

    def _get_most_similar_user(self, seen: dict[str, list[tuple[str, str]]]) -> str:
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
        >>> graph._get_most_similar_user({})
        'user_3'
        >>> graph._get_most_similar_user({'user_3': [('Kiss of Life', 'Sade')]})
        'user_2'
        >>> graph_2 = Graph()
        >>> graph_2.add_user_vertex("user_1", True)
        >>> graph_2.add_user_vertex("user_2", False)
        >>> graph_2._get_most_similar_user({})
        'user_1'
        """
        connected_users = self._get_connected_users()
        most_similar_user = self.user_vertex_id
        max_score_so_far = 0

        for user_id in connected_users:
            # if the number of connections is the same as the number of neighbours of the current user's id
            # then there are no new recommendations to be
            if len(self._user_vertices[user_id].neighbours) == connected_users[user_id]:
                continue
            elif user_id in seen and connected_users[user_id] == (len(self._user_vertices[user_id].neighbours)
                                                                  - len(seen[user_id])):
                # if we've seen every song recommendation in the current user vertex, skip over it
                # number of connections is equal to the number of neighbours - songs we've seen
                continue
            else:
                if connected_users[user_id] > max_score_so_far:
                    most_similar_user = user_id
                    max_score_so_far = connected_users[user_id]

        return most_similar_user

    def _get_song_recs(self, similar_user: str, seen: dict[str, list[tuple[str, str]]]) -> list[tuple[str, str]]:
        """
        This method returns a set of three song ids per similar user which
        are not currently in the user's currently saved songs (neighbours)
        - This includes URL for the songs

        The first item in the returned list is the id for the similar user

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
        >>> graph._get_song_recs("user_3", {})
        ['user_3', ('Kiss of Life', 'Sade')]
        >>> graph._get_song_recs("user_3", {'user_3': [('Kiss of Life', 'Sade')]})
        ['user_3']
        """
        lst_so_far = [similar_user]

        song_ids_seen = {song_info[0] + song_info[1] for user in seen for song_info in seen[user]}

        for song in self._user_vertices[similar_user].neighbours:
            if (song not in self._user_vertices[self.user_vertex_id].neighbours and
                    song.item + song.artist not in song_ids_seen):
                lst_so_far.append((song.item, song.artist))

        return lst_so_far

    def get_recommendations(self, seen: dict[str, list[tuple[str, str]]], limit: int = 5) -> list[str
                                                                                                  | tuple[str, str]]:
        """
        This method returns recommendations to the user based on their listened to songs.
        The method returns a list of tuples of two string: one is the song title, the other is the song url.
        Three nested lists of tuples -- going from most simiular songs

        Returns an empty list if there are no similar users

        TODO - doctests
        TODO - preconditions


        HOW TO IMPLEMENT SEEN:
        seen = {}
        h = my_graph.get_recommendations(seen)

        (You press on the button)
        if h[0] not in seen:
            seen[h[0]] = [song_value for song_value in h[1:]]
        else:
            seen[h[0]] += [song_value for song_value in h[1:]]

        h = my_graph.get_recommendations(seen)

        Preconditions:
            - limit >= 0

        >>> graph = Graph()
        >>> graph.add_user_vertex("user_1", True)
        >>> graph.add_user_vertex("user_2", False)
        >>> graph.add_user_vertex("user_3", False)
        >>> graph.add_song_vertex("Let Down", "Radiohead")
        >>> graph.add_song_vertex("Kiss of Life", "Sade")
        >>> graph.add_song_vertex("Sunday", "The Cranberries")
        >>> graph.add_song_vertex("Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_1", "Let Down", "Radiohead")
        >>> graph.add_edge("user_2", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_2", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Kiss of Life", "Sade")
        >>> graph.add_edge("user_3", "Dreams", "The Cranberries")
        >>> graph.add_edge("user_3", "Let Down", "Radiohead")
        >>> graph.add_edge("user_3", "Sunday", "The Cranberries")
        >>> recommendations_1 = graph.get_recommendations({})
        >>> set(recommendations_1) == {'user_3', ('Kiss of Life', 'Sade'), ('Sunday', 'The Cranberries')}
        True
        >>> recommendations_1[0] == 'user_3'
        True
        >>> graph.get_recommendations({'user_3': [('Kiss of Life', 'Sade'), ('Sunday', 'The Cranberries')]})
        ['user_2']
        """
        similar_user = self._get_most_similar_user(seen)
        if similar_user == self.user_vertex_id:
            return []

        recommendation_results = self._get_song_recs(similar_user, seen)
        return recommendation_results[0:limit]


def _load_curr_user_songs(spotify_info: Spotify, graph: Graph) -> bool:
    """
    Loads the current user's songs into the graph
    """
    curr_user_tracks = spotify_info.current_user_saved_tracks(limit=50)

    if curr_user_tracks is None:
        return False

    graph.add_user_vertex("current_user", True)
    for track_info in curr_user_tracks['items']:
        title = track_info['track']['name']
        artist = track_info['track']['album']['artists'][0]['name']

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
    """
    graph_so_far = Graph()
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
    auth = oauth_activation.SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
    auth.setup_auth_manager()
    spot_test = auth.authenticate()
    # except ():
    # spot_test = None

    my_graph = load_song_listening_graph('spotify_dataset.csv', spot_test)

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ["spotipy", "oauth_activation", "__future__", "csv", "typing", "networkx"],
    #     'allowed-io': ["load_song_listening_graph", "_load_hardcoded_user_songs"],
    #     'max-line-length': 120,
    #     'max-nested-blocks': 4
    # })
