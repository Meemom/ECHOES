"""
Author: Julia Sinclair
Date: 2025-03-31
Desc: This file contains the code for the recommnder graph element of our project. Included in this
file is the _Vertex and Graph classes that we will be using in our main function.

"""
from __future__ import annotations
import csv
from typing import Any, Optional

from spotipy import Spotify
import oauth_activation


class _UserVertex:
    """
    This class defines the vertex of the graph for the spotify recommender. This class
    represents the general user vertices in the recommender graph.

    Instance Attributes:
        - item: The data stored in this vertex - in this case user_id.
        - neighbours: The song vertices that are adjacent to this user vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: set[_SongVertex]

    def __init__(self, item: Any, neighbours: set[_SongVertex]) -> None:
        """
        This is the initializer method for this class -- setting the vertex with given item
        and given neighbours.
        """
        self.item = item
        self.neighbours = neighbours


class _SongVertex:
    """
    This class defines the vertices for songs in the recommender graph

    Instance Attributes:
        - title: a string value representing the title of the song
        - artist: a string value representing the name of the artist of the song
        - neighbours: The user vertices that are adjacent to this user vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    title: str
    artist: str
    neighbours: set[_UserVertex]

    def __init__(self, song_title: str, artist: str, neighbours: set[_UserVertex]) -> None:
        """
        This initializer method creates an instance of the _SongVertex class with the given
        song_title, artist, and neighbours
        """
        self.title = song_title
        self.artist = artist
        self.neighbours = neighbours


class Graph:
    """
    This graph connects two types of vertices: songs and their associated listeners. This graph
    represents a network of songs and the listeners to those songs. This network highlights
    one user vertex -- which is the current user's vertex -- to find recommendations for the current user

    Instance Attributes:
        - user_vertex_id: the id of the user vertex representing the current user using the program

    (Private) Instance Attributes:
        - _user_vertices: a dictionary mapping the item/username of a user vertices to its
        associated _UserVertex object
        - _song_vertices: a dictionary mapping the string id of the song (in the format
        "title:<song_title>artist:<artist_name>") to the associated _SongVertex object
    """
    user_vertex_id: Optional[str]
    _user_vertices: dict[Any, _UserVertex]
    _song_vertices: dict[str, _SongVertex]

    def __init__(self) -> None:
        """
        The initializer method for Graph. This method creates a graph object and sets it's
        values to the default values for an empty graph.
        """
        self.user_vertex_id = None
        self._song_vertices = {}
        self._user_vertices = {}

    def add_edge(self, username: str, song_title: str, artist: str) -> None:
        """
        This method creates an edge between the user vertex with the specified username and the
        song vertex with the specified song_title and artist.
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
        This method adds a song vertex to the graph with the given title and artist.

        This song vertex is not adjacent to any user vertices. If the vertex is already in
        the graph, the method does not modify the current song vertices.
        """
        song_id = "title:" + title + "artist:" + artist
        if song_id not in self._song_vertices:
            self._song_vertices[song_id] = _SongVertex(title, artist, set())

    def add_user_vertex(self, item: Any, main_user: bool) -> None:
        """
        This method adds a user vertex to the graph with the given item and whether
        the vertex is the vertex of the current user depending on the given main_user parameter.
        """
        if item not in self._user_vertices:
            self._user_vertices[item] = _UserVertex(item, set())

        if main_user:
            self.user_vertex_id = item

    def _get_connected_users(self) -> dict[Any, int]:
        """
        This method gets all connected users who are connected with one song vertex in between them and the user
        vertex for the current user.

        Returns a dictionary mapping of the username of the user to the number of song vertices they share
        as neighbours with the current user vertex.

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
        This method returns a username for a user with the highest similarity score to the current_user.
        The similarity score is based on how many neighbours that vertex has in common with the current user's
        vertex.

        The username that is returned has at least one unique song that is NOT a neighbour of the current user's
        vertex and has available songs to be recommended that are not already in the seen dictionary -- which maps
        user id to a list of tuples of song names and artist names that have been recommended before.

        Returns the current user vertex id if there are NO CONNECTED USERS.

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
        This method returns a list of tuples of song titles and their artists for the given similar
        are not currently in the user's currently saved songs (neighbours) and not currently in the values for the
        key-value pairs of seen.

        The first item in the returned list is the id for the similar user. Will return a list of
        only this item if there are no possible song recommendations.

        Preconditions:
            - similar_user in self._user_vertices

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
            if (song not in self._user_vertices[self.user_vertex_id].neighbours
                    and song.title + song.artist not in song_ids_seen):
                lst_so_far.append((song.title, song.artist))

        return lst_so_far

    def get_recommendations(self, seen: dict[str, list[tuple[str, str]]], limit: int = 5) -> list[str
                                                                                                  | tuple[str, str]]:
        """
        This method returns recommendations to the user based on the songs they listened to and the
        listening habits of other users in the graph, with a default of 5 recommendations returned.

        Returns an empty list if there are no similar songs.

        Otherwise, returns a list of strings and tuples of two strings:
        - the item at index 0 is the username of the user that these songs are recommended from
        - the following tuples consist of two items, the first is the title of the song and the second is the
        name of the artist

        Preconditions:
            - limit >= 0
            - all("title:" + song_info[0] + "artist:" + song_info[1] in self._song_vertices \
            for user in seen for song_info in seen[user])
            - all("title:" + song_info[0] + "artist:" + song_info[1] in self._user_vertices[user].neighbours \
            for user in seen for song_info in seen[user])

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
        []
        """
        similar_user = self._get_most_similar_user(seen)
        recommendation_results = self._get_song_recs(similar_user, seen)

        if similar_user == self.user_vertex_id or len(recommendation_results) == 1:
            return []

        return recommendation_results[0:limit]


def _load_curr_user_songs(spotify_info: Spotify, graph: Graph) -> bool:
    """
    Loads the current user's songs into the graph using information obtained from the given spotify_info.
    Returns True if the current user has saved songs and returns False otherwise.
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


def _load_hardcoded_user_songs(user_data_csv: str, graph: Graph) -> None:
    """
    Loads a data set of songs representing what the current user listens to.
    This is for demo purposes.

    Preconditions:
        - user_data is the path to a CSV file corresponding to the data set of songs the user has listened to
          with the format of comma-seperated values in this order: song name, artist name
    """
    graph.add_user_vertex("current_user", True)

    with open(user_data_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            graph.add_song_vertex(row[0], row[1])
            graph.add_edge("current_user", row[0], row[1])


def load_song_listening_graph(listening_info_file: str, spotify_info: Optional[Spotify] = None,
                              user_data: Optional[str] = None) -> Graph:
    """
    This method returns a graph based on the given data set called listening_info_file and the current user's
    profile information given by spotify_info or user_data depending on whether the authentification
    for the spotify API happens properly.

    Preconditions:
        - listening_info_file is the path to a CSV file corresponding to the data set of songs with the format
          of the first line being the header, and the following having comma-seperated values in this order:
          user_id, artist name, song name, playlist the song is being listened to in
        - user_data is the path to a CSV file corresponding to the data set of songs the user has listened to
          with the format of comma-seperated values in this order: song name, artist name
        - spotify_info is None == user_data is not None
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
            if limit == 1000000:
                break

            graph_so_far.add_song_vertex(row[2], row[1])

            if row[0] not in users_so_far:
                graph_so_far.add_user_vertex(row[0], False)
                users_so_far.add(row[0])

            graph_so_far.add_edge(row[0], row[2], row[1])
            limit += 1

    # _load_hardcoded_user_songs(graph_so_far) if the spot_test is not working
    result = False
    if spotify_info is not None:
        result = _load_curr_user_songs(spotify_info, graph_so_far)

    if result is False or spotify_info is None:
        _load_hardcoded_user_songs(user_data, graph_so_far)

    # final return statement
    return graph_so_far


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    CLIENT_ID = "d4438951382c4c05bceb265fd8de11ec"
    CLIENT_SECRET = "f6890c57cc42499581c685cd79dadded"
    REDIRECT_URI = "http://localhost:8888/callback"
    SCOPE = "user-library-read"
    CACHE_PATH = ".spotify_cache"

    auth = oauth_activation.SpotifyAuthentication(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
    auth.setup_auth_manager()
    spot_test = auth.authenticate()

    if spot_test is None:
        my_graph = load_song_listening_graph('spotify_dataset.csv', user_data="data_user.csv")
    else:
        my_graph = load_song_listening_graph('spotify_dataset.csv', spot_test)

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ["spotipy", "oauth_activation", "__future__", "csv", "typing", "networkx"],
        'allowed-io': ["load_song_listening_graph", "_load_hardcoded_user_songs"],
        'max-line-length': 120,
        'max-nested-blocks': 4
    })
