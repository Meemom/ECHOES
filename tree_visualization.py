import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import export_graphviz
import graphviz
from updated_decision_tree import DecisionTree

def visualize_tree(dtree: DecisionTree, feature_names: list[str], filename: str = "tree visualization"):
    """Visualizes the decision tree and saves it to a file."""

    dot_data = export_graphviz(dtree.root, out_file=None,
                               feature_names=feature_names,
                               class_names=dtree.classes_,
                               filled=True, rounded=True,
                               special_characters=True)

    graph = graphviz.Source(dot_data)

    graph.render(output_file, format='png', cleanup=True)

    print(f"Decision tree visualized and saved to {output_file}.png")


visualize_tree(dtree=clf, feature_names=FEATURES, output_file="spotify_recommendation_tree")




