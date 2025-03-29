"""
CSC111 Project 2: Spotify Recommendation System - GUI Module
This module handles the GUI for the Spotify Recommendation System, including user interactions and displaying results.
"""

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

from tkinter import Frame, StringVar, Tk, E, N, S, W
from tkinter.ttk import Button, Entry, Label

class Application(Tk):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.title("Hello World")
        self.geometry("600x100")
        self.resizable(width = False, height = False)

        HelloWorld(self).grid(sticky = (E + W + N + S))
        self.columnconfigure(0, weight = 1)

class HelloWorld(Frame):

    def __init__(self, parent, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)

        self.name = StringVar()
        self.hello_message = StringVar(value = "Hello!")

        name_label = Label(self, text = "Name")
        name_textbox = Entry(self, textvariable = self.name)
        name_button = Button(self, text = "Set", command = self.set_name)

        hello_label = Label(self, textvariable = self.hello_message)

        name_label.grid(row = 0, column = 0, sticky = W)
        name_textbox.grid(row = 0, column = 1, sticky = (E + W))
        name_button.grid(row = 0, column = 2, sticky = E)
        hello_label.grid(row = 1, column = 1, columnspan = 3)

        self.columnconfigure(1, weight=1)

    def set_name(self):

        if self.name.get():
            self.hello_message.set("Hello " + self.name.get())
        else:
            self.hello_message.set("Hello World")



# main loop
if __name__ == "__main__":
    app = Application()
    app.mainloop()



#  PRACTICE CODE, IGNORE


# def on_click():
#     lbl.config(text="Button clicked!")


# lbl = tk.Label(root, text="Label 1")
# lbl.grid(row=0, column=0)

# print(lbl.config().keys())  # view all available options for the label widget

# btn = tk.Button(root, text="Button 1", command=on_click)
# btn.grid(row=0, column=1)   

# tk.mainloop()