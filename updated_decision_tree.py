"""CSC111 Project 2: Spotify Recommendation System - Decision Tree

This module contains functions for fitting a decision tree to a music dataset,
enabling song recommendations based on a randomly selected song.
"""

# Standard Library imports
import os
import random
from collections import Counter
from typing import Any, Optional
import python_ta

# Third-Party Library imports
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import graphviz
from graphviz import Source


class Node:
    """A class representing a node in the decision tree.

    Instance Attributes:
        - feature: The index of the feature (column) used to split the data at this node.
        - threshold: The threshold value for the feature used to split the data.
        - left: The left child node.
        - right: The right child node.
        - value: The class label or predicted value of the node. This is used only in leaf nodes.
        It is the majority class or predicted label at this node.
    """
    feature: Optional[int]
    threshold: Optional[float]
    left: Optional['Node']
    right: Optional['Node']
    value: Optional[Any]

    def __init__(self, feature=None, threshold=None, left=None, right=None,*,value=None) -> None:
        """Initialize a Node class."""
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def is_leaf_node(self) -> None:
        """Returns whether the node is a leaf node."""
        return self.value is not None


class DecisionTree:
    """A class representing a decision tree that manages the song recommendation system.

    Instance Attributes:
        - min_samples_split: The minimum number of samples required to split an internal node.
        - max_depth: The maximum depth of the decision tree. Limits the tree's growth to prevent overfitting.
        - n_features: The number of features to consider when looking for the best split.
        If None, all features are considered.
        - root: The root node of the decision tree.
    """
    min_samples_split: int
    max_depth: int
    n_features: Optional[int]
    root: Optional[Node]

    def __init__(self, min_samples_split=10, max_depth=5, n_features=None) -> None:
        """Initializes a DecisionTree class."""
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        self.n_features = n_features
        self.root = None

    def fit(self, X, y) -> None:
        """Fits a decision tree to the dataset."""
        # check that self.n_features is not more than the actual number of features
        self.n_features = X.shape[1] if not self.n_features else min(X.shape[1], self.n_features)
        self.root = self._grow_tree(X, y)  # builds a decision tree based on the training data

    def _grow_tree(self, X, y, depth=0) -> Node:
        """Recursively grows the decision tree."""
        n_samples, n_feats = X.shape  # get the number of samples and the number of features in the current node
        n_labels = len(np.unique(y))  # get the number of unique labels in the target variable

        # check the stopping criteria
        if depth >= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split:
            # stop growing and return the most common label at this node
            leaf_value = self._most_common_label(y)
            return Node(value=leaf_value)

        # only select unique features
        feat_idxs = np.random.choice(n_feats, self.n_features, replace=False)

        # find the best split
        best_feature, best_threshold = self._best_split(X, y, feat_idxs)

        # create child nodes
        left_idxs, right_idxs = self._split(X[:, best_feature], best_threshold)
        left = self._grow_tree(X[left_idxs, :], y[left_idxs], depth + 1)
        right = self._grow_tree(X[right_idxs, :], y[right_idxs], depth + 1)

        return Node(feature=best_feature, threshold=best_threshold, left=left, right=right)

    def _best_split(self, X, y, feat_idxs) -> tuple[Optional[int], Optional[float]]:
        """Find the best threshold among all possible thresholds."""
        best_gain = -1
        split_idx, split_threshold = None, None

        for feat_idx in feat_idxs:
            X_column = X[:, feat_idx]
            thresholds = np.unique(X_column)

            for threshold in thresholds:
                # calculate the information gain
                gain = self._information_gain(y, X_column, threshold)

                if gain > best_gain:
                    best_gain = gain
                    split_idx = feat_idx
                    split_threshold = threshold

        return split_idx, split_threshold

    def _information_gain(self, y, X_column, threshold) -> float:
        """Compute the information gain from splitting a dataset at a given threshold.

        Preconditions:
            - y.size > 0
            - X.column.size == y.size
        """
        # parent entropy
        parent_entropy = self._entropy(y)

        # create children
        left_idxs, right_idxs = self._split(X_column, threshold)

        if len(left_idxs) == 0 or len(right_idxs) == 0:  # check if either are empty
            return 0

        # calculate weighted entropy of children
        n = len(y)
        n_left, n_right = len(left_idxs), len(right_idxs)
        entropy_left, entropy_right = self._entropy(y[left_idxs]), self._entropy(y[right_idxs])
        child_entropy = (n_left/n) * entropy_left + (n_right/n) * entropy_right

        # calculate information gain
        information_gain = parent_entropy - child_entropy
        return information_gain

    def _split(self, X_column, split_threshold) -> tuple[np.ndarray, np.ndarray]:
        """Split the dataset into two groups based on the given split_threshold.

        Preconditions:
            - X.column.size > 0
        """
        left_idxs = np.argwhere(X_column <= split_threshold).flatten()
        right_idxs = np.argwhere(X_column > split_threshold).flatten()
        return left_idxs, right_idxs

    def _entropy(self, y) -> float:
        """Calculate the entropy of a given set of labels.

        The entropy is a measure of the impurity or uncertainty in the labels.
        It ranges from 0 (no uncertainty) to log2(n) (maximum uncertainty).
        """
        hist = np.bincount(y)
        prob = hist / len(y)
        return -np.sum(prob * np.log2(prob + 1e-9))

    def _most_common_label(self, y) -> Optional[int]:
        """Find the most common label in the dataset."""
        if len(y) == 0:
            return None
        counter = Counter(y)
        return counter.most_common(1)[0][0]

    def predict(self, X) -> np.array:
        """Predict class labels for a given dataset using the trained decision tree.

        Preconditions:
            - self.root is not None
        """
        return np.array([self._traverse_tree(x, self.root) for x in X])

    def _traverse_tree(self, x, node) -> int:
        """Recursively traverse the decision tree to classify a single sample.

        If the current node is a leaf, return its stored class label. Otherwise, continue
        traversing based on the feature's threshold.

        Preconditions:
            - node is not None
            - x.size > 0 (the input sample must have at least one feature)
        """
        if node.is_leaf_node():  # base case
            return node.value
        else:
            if x[node.feature] <= node.threshold:
                return self._traverse_tree(x, node.left)
            else:
                return self._traverse_tree(x, node.right)


def recommend_songs(dtree: DecisionTree, user_song: str, features: list[str],
                    dataset: pd.DataFrame, top_n=5) -> Optional[list[tuple]]:
    """Recommend a similar song to the given user_song using the decision tree dtree and cosine similarity.

    Preconditions:
        - dtree is a trained DecisionTree object
        - user_song is a valid song name in the dataset
        - features is a list of feature names that exist in the dataset
        - dataset is a pandas DataFrame containing at least the column names: 'name', 'artists'
        and the specified features.
        - top_n > 0 (default value is returning the top 5 recommended songs).
    """

    # find user_song features in the dataset
    user_song_features = get_song_features(user_song, features, dataset)

    # get the leaf nodes of the decision
    user_song_features_df = pd.DataFrame([user_song_features])
    leaf_node_prediction = dtree.predict(user_song_features_df.to_numpy())[0]

    # using LabelEncoder to map the leaf node back to the song name
    le = LabelEncoder()
    le.fit(dataset['name'])  # fit the encoder on the dataset's song names
    predicted_song_name = le.inverse_transform([leaf_node_prediction])[0]

    # extract songs that belong to the predicted leaf node
    leaf_node_songs = dataset[dataset['name'] == predicted_song_name]

    # remove duplicates
    leaf_node_songs = leaf_node_songs.drop_duplicates(subset='name')

    if len(leaf_node_songs) == 0:
        print("No songs found in this leaf node.")
        return None

    # begin finding similar songs
    similarities = []
    user_song_vector = np.array(list(user_song_features.values())).reshape(1, -1)

    for index, row in leaf_node_songs.iterrows():
        song_features = row.to_dict()
        song_features_values = {k: v for k, v in song_features.items() if k in user_song_features}
        song_vector = np.array(list(song_features_values.values())).reshape(1, -1)

        similarity = calculate_cosine_similarity(user_song_vector, song_vector)  # using helper function below
        song_name = row['name'].strip()  # ensure no extra whitespace
        artist_name = row['artists']
        similarities.append((song_name, artist_name, similarity))  # append song name, artist, and similarity

    # rank and filter by similarity
    similarities = [item for item in similarities if item[2] != -1]  # filter out invalid similarities
    similarities.sort(key=lambda x: x[2], reverse=True)

    # remove duplicates
    seen = set()
    recommended_songs = []
    for song, artists, similarity in similarities:
        if song not in seen:
            recommended_songs.append((song, artists, similarity))
            seen.add(song)

    return recommended_songs

def calculate_cosine_similarity(user_song_vector, song_vector) -> float:
    """Calculates the cosine similarity between the feature vectors of the user's song and a song from the dataset.
    If the shapes of the feature vectors for the user song and dataset song do not match, it returns -1.
    """
    if user_song_vector.shape == song_vector.shape:  # check if user song and dataset song have the same dimensions
        return cosine_similarity(user_song_vector, song_vector)
    else:
        return -1  # default value for missing similarity


def get_song_features(user_song: str, features: list[str], dataset: pd.DataFrame) -> dict[str, float]:
    """Returns the feature values for a specific song from the dataset.

    Representation Invariants:
        - `dataset` must contain a 'name' column and all features specified in `features`.
        - All elements in `features` must be valid column names in `dataset`.
    """

    # filter the dataset to get the row corresponding to user_song
    song_row = dataset[dataset['name'] == user_song]

    if song_row.empty:
        raise ValueError(f"Song '{user_song}' not found in the dataset.")

    # extract the requested features for the song and convert to a dictionary
    user_song_features = song_row[features].iloc[0].to_dict()

    return user_song_features


def visualize_custom_tree(node, feature_names, class_names, dot_data=None, parent=None, depth=0):
    """Recursively traverse the tree and create Graphviz dot representation."""
    if dot_data is None:
        dot_data = "digraph Tree {\n"  # indicates start of the tree representation

    if node.is_leaf_node():  # if it is a leaf node, label with class name
        class_name = class_names[node.value]
        class_name = class_name.replace('"', '\\"')  # get rid of quotes in class name
        dot_data += f'    node{depth} [label="{class_name}"];\n'
        if parent is not None:  # if the node is not the root, add edge between parent node to current leaf node
            dot_data += f'    node{parent} -> node{depth};\n'
    else:  # if it is an internal node, label with feature names and thresholds
        feature_name = feature_names[node.feature]
        feature_name = feature_name.replace('"', '\\"')  # get rid of quotes in class name
        dot_data += f'    node{depth} [label="{feature_name} <= {node.threshold:.2f}"];\n'
        if parent is not None:
            dot_data += f'    node{parent} -> node{depth};\n'

        dot_data = visualize_custom_tree(node.left, feature_names, class_names, dot_data, parent=depth, depth=depth + 1)
        dot_data = visualize_custom_tree(node.right, feature_names, class_names, dot_data, parent=depth, depth=depth + 1)

    if depth == 0:  # once all the nodes and edges are processed
        dot_data += "}\n"
        return Source(dot_data)

    return dot_data  # return dot data when the function is not at root level (i.e. depth > 0)


def plot_tree(dtree, feature_names, class_names, filename='tree'):
    """Generate the tree visualization and save to a file."""
    graph = visualize_custom_tree(dtree.root, feature_names, class_names)
    print(graph.source)
    graph.render(filename, format='png')
    print(f"Tree visualization saved to {filename}.png")


if __name__ == "__main__":
    # python_ta.check_all(config={
    #     'extra-imports': [
    #         'os', 'random', 'collections', 'typing', 'numpy', 'pandas',
    #         'sklearn.model_selection', 'sklearn.metrics', 'sklearn.metrics.pairwise',
    #         'sklearn.preprocessing', 'graphviz', 'python_ta'
    #     ],
    #     'allowed-io': ['plot_tree', 'recommend_songs'],
    #     'max-line-length': 120
    # })

    # define constants for the features used in the model and the dataset limit
    FEATURES = ['speechiness', 'tempo', 'energy', 'loudness', 'acousticness', 'danceability', 'instrumentalness']
    LIMIT = 5000  # limit the dataset size to LIMIT rows to reduce running time during testing

    # DATA WRANGLING
    df = pd.read_csv('path-to-file/songs_with_attributes_and_lyrics.csv')  # TODO: replace path-to-file
    df = df.dropna(subset=FEATURES)
    df = df.head(LIMIT)

    # generating a random index for demo purposes
    random_index = random.randint(0, LIMIT)

    # retrieve the song name at the random index
    SONG = df.iloc[random_index]['name']
    ARTISTS = df.iloc[random_index]['artists']
    print(f"Searching for similar songs for '{SONG}' by {ARTISTS}")

    print(f"Searching through {df.shape[0]} songs...")

    # convert pandas DataFrame (X) and pandas Series (y) to numpy arrays
    X = df[FEATURES].to_numpy()
    y = df['name'].to_numpy()  # the target value is song

    # encode the 'song' column as categories
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    class_names = le.classes_.tolist()

    assert np.min(y_encoded) >= 0, "y should contain non-negative values"

    # split the data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=1011201502)

    # initialize the decision tree
    clf = DecisionTree(min_samples_split=2, max_depth=7)
    clf.fit(X_train, y_train)

    # (Optional) visualize tree
    plot_tree(dtree=clf, feature_names=FEATURES, class_names=class_names, filename="song_recommendation_tree")

    # get song recommendations
    # get song recommendations
    recommended_songs = recommend_songs(dtree=clf, user_song=SONG, features=FEATURES, dataset=df)

    print("Recommended songs:")
    for song, artists, _ in recommended_songs:
        print(f"Song: {song}, Artist: {artists}")

    # (Optional) evaluate the accuracy of the model on the test set
    # the accuracy is based on the dataset's constraints
    accuracy = accuracy_score(y_test, clf.predict(X_test))
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
