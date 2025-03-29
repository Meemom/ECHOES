"""
CSC111 Project 2: Spotify Recommendation System - Login Module
This module handles the login page.
"""

import tkinter as tk
from customtkinter import *
from PIL import Image
import sys

# image files
icon = Image.open("GUI/icon.png")
icon.save("GUI/icon.ico", format="ICO")
logo = Image.open("GUI/logo.png")
logo_ctk = CTkImage(light_image=logo, size=(512,125))  # Adjust size as needed

# Setting theme and appearance
set_appearance_mode("dark")
set_default_color_theme("green")

# initialize the main window
root = CTk()
root.title("ECHOES")
root.resizable(False, False)
root.geometry("600x480")
root.iconbitmap("GUI/icon.ico")

# set the widgets, labels, text, etc
logo_label = CTkLabel(root, image=logo_ctk, text="")
logo_label.pack(pady=75)

welcome = CTkLabel(root,
                    text="Welcome!", 
                    text_color="white",
                    font=("Coolvetica", 40)
                   )
welcome.pack(pady=0)

request = CTkLabel(root,
                    text="Please login to continue", 
                    text_color="white",
                    font=("Helvetica", 20)
                   )
request.pack(pady=0)

login_button = CTkButton(root,
                    text="Login", 
                    command=NotImplementedError,
                    height=50,
                    width=512,
                    corner_radius=32,
                    font=("Coolvetica", 20)
)
login_button.pack(pady=25)



# main loop
if __name__ == "__main__":
    root.mainloop()
    # oauth.app.run()
