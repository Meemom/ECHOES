import tkinter as tk
from tkinter import messagebox, simpledialog
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from oauth_activation import Flask

# TODO: fix docstrings and invariants

# constants
client_id = "f8f5475f76b6492d865574179fb39c3b"
client_secret = "a6eb99e6534d4625ab7f78cef37f091b"
redirect_uri = "http://localhost:5000/callback"

root = tk.Tk()
root.title("Song Recommendation System")

class SpotifyManager:
    """
    Manager class that handles Spotify authentication and API requests.
    """
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope='user-library-read playlist-modify-private'  # TODO: subject to change, discuss w/ others first
        )

    def run(self):
        """
        handle run command for mainloop
        """
        self.root.mainloop()



# main loop
if __name__ == "__main__":
    app = SpotifyManager(client_id, client_secret, redirect_uri)
    app.run()



#  PRACTICE CODE, IGNORE


# def on_click():
#     lbl.config(text="Button clicked!")


# lbl = tk.Label(root, text="Label 1")
# lbl.grid(row=0, column=0)

# print(lbl.config().keys())  # view all available options for the label widget

# btn = tk.Button(root, text="Button 1", command=on_click)
# btn.grid(row=0, column=1)   
