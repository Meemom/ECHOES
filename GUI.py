"""
CSC111 Project 2: Spotify Recommendation System - GUI Module
This module handles the GUI for the Spotify Recommendation System, including user interactions and displaying results.
"""

import tkinter as tk
from customtkinter import *
from PIL import Image

# Setting theme and appearance
set_appearance_mode("dark")
set_default_color_theme("green")

root = CTk()
# root.title("TBA")   # TODO: add title
# root.iconbitmap("TBA")  # TODO: add icon
root.geometry("600x350")

my_button = CTkButton(root, text="Hello World", command=lambda: print("Button clicked!"))
my_button.pack(pady=20)

# main loop
if __name__ == "__main__":
    root.mainloop()



#  PRACTICE CODE, IGNORE


# def on_click():
#     lbl.config(text="Button clicked!")


# lbl = tk.Label(root, text="Label 1")
# lbl.grid(row=0, column=0)

# print(lbl.config().keys())  # view all available options for the label widget

# btn = tk.Button(root, text="Button 1", command=on_click)
# btn.grid(row=0, column=1)   

# tk.mainloop()