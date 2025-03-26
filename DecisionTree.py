class Tree:
    """A Tree that represents the recommended songs from a given song based on different categories.

    Instance Attributes:
        - _root: The item stored at the tree's root, which represents the given song by the user.
        - _subtrees:
        """
    _root: str
    _subtrees: list[Tree]

    def __init__(self):
