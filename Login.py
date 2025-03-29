"""
CSC111 Project 2: Spotify Recommendation System - Login Module
This module handles the login page and OAuth authentication.
"""

import tkinter as tk
from customtkinter import *
from PIL import Image
import sys
import threading
import webbrowser
import oauth_activation as oauth
from flask import Flask

# image files
icon = Image.open("icon.png")
icon.save("icon.ico", format="ICO")
logo = Image.open("logo.png")
logo_ctk = CTkImage(light_image=logo, size=(512,125))

# setting theme and appearance
set_appearance_mode("dark")
set_default_color_theme("green")

def start_oauth_server():
    """Start the Flask server for OAuth in a separate thread"""
    oauth.app.run(debug=False)

def open_login_page():
    """Open the Spotify login page in the default web browser"""
    # create and start the Flask server thread
    server_thread = threading.Thread(target=start_oauth_server)
    server_thread.daemon = True  # make thread exit when main program exits
    server_thread.start()
    
    # create authenticator and get the auth URL
    authenticator = oauth.SpotifyAuthentication(
        oauth.CLIENT_ID, 
        oauth.CLIENT_SECRET, 
        oauth.REDIRECT_URI, 
        oauth.SCOPE
    )
    authenticator.setup_auth_manager()
    auth_url = authenticator.get_auth_url()
    
    # open the auth URL in the default browser
    webbrowser.open(auth_url)
    
    # update UI to show login in progress
    login_button.configure(text="Logging in...", state="disabled")
    request.configure(text="Authorization in progress. Please check your browser.")

# initialize the main window
root = CTk()
root.title("ECHOES")
root.resizable(False, False)
root.geometry("600x480")
root.iconbitmap("icon.ico")

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
                    command=open_login_page,  # connection to login function
                    height=50,
                    width=512,
                    corner_radius=32,
                    font=("Coolvetica", 20)
)
login_button.pack(pady=25)

# main loop
if __name__ == "__main__":
    root.mainloop()

"""
ALTERNATIVE, IGNORE TODO: check whether you want to use this or not.
"""

# import tkinter as tk
# from customtkinter import *
# from PIL import Image
# import sys
# import threading
# import webbrowser
# import oauth_activation as oauth
# from flask import Flask
# import os
# import json
# import time

# # image files
# icon = Image.open("icon.png")
# icon.save("icon.ico", format="ICO")
# logo = Image.open("logo.png")
# logo_ctk = CTkImage(light_image=logo, size=(512,125))  # Adjust size as needed

# # Status file path
# AUTH_STATUS_FILE = "auth_status.json"

# # Setting theme and appearance
# set_appearance_mode("dark")
# set_default_color_theme("green")

# def start_oauth_server():
#     """Start the Flask server for OAuth in a separate thread"""
#     # First, modify the userdata route to write the status file
#     def custom_userdata():
#         authenticator = oauth.SpotifyAuthentication(
#             oauth.CLIENT_ID, oauth.CLIENT_SECRET, oauth.REDIRECT_URI, oauth.SCOPE
#         )
#         authenticator.setup_auth_manager()
        
#         if not authenticator.validate_token():
#             auth_url = authenticator.get_auth_url()
#             return oauth.redirect(auth_url)

#         spotify = oauth.Spotify(auth_manager=authenticator.auth_manager)
#         user = spotify.current_user()
        
#         # Write authentication status to file
#         status_data = {
#             "authenticated": True,
#             "display_name": user["display_name"],
#             "user_id": user["id"]
#         }
        
#         with open(AUTH_STATUS_FILE, 'w') as f:
#             json.dump(status_data, f)
        
#         return oauth.jsonify({
#             "status": "success", 
#             "message": "Authentication complete. You can close this window and return to the application."
#         })
    
#     # Replace the userdata route with our custom one
#     oauth.app.view_functions['userdata'] = custom_userdata
    
#     # Start the Flask server
#     oauth.app.run(debug=False)

# def check_auth_status():
#     """Check if authentication is complete by looking for status file"""
#     if os.path.exists(AUTH_STATUS_FILE):
#         try:
#             with open(AUTH_STATUS_FILE, 'r') as f:
#                 status_data = json.load(f)
                
#             if status_data.get('authenticated', False):
#                 # Authentication successful - update UI and proceed
#                 login_button.configure(text="Login Successful!", state="disabled")
#                 request.configure(text=f"Welcome, {status_data.get('display_name', 'User')}!")
                
#                 # In a real app, you would transition to the main screen here
#                 # For example: open_main_screen(status_data)
                
#                 return False  # Stop checking
            
#         except Exception as e:
#             print(f"Error reading status file: {e}")
    
#     # Continue checking if not authenticated yet
#     root.after(1000, check_auth_status)
#     return True

# def open_login_page():
#     """Open the Spotify login page in the default web browser"""
#     # Remove status file if it exists from previous sessions
#     if os.path.exists(AUTH_STATUS_FILE):
#         os.remove(AUTH_STATUS_FILE)
    
#     # Create and start the Flask server thread
#     server_thread = threading.Thread(target=start_oauth_server)
#     server_thread.daemon = True  # Make thread exit when main program exits
#     server_thread.start()
    
#     # Create authenticator and get the auth URL
#     authenticator = oauth.SpotifyAuthentication(
#         oauth.CLIENT_ID, 
#         oauth.CLIENT_SECRET, 
#         oauth.REDIRECT_URI, 
#         oauth.SCOPE
#     )
#     authenticator.setup_auth_manager()
#     auth_url = authenticator.get_auth_url()
    
#     # Give the server a moment to start
#     time.sleep(1)
    
#     # Open the auth URL in the default browser
#     webbrowser.open(auth_url)
    
#     # Update UI to show login in progress
#     login_button.configure(text="Logging in...", state="disabled")
#     request.configure(text="Authorization in progress. Please check your browser.")
    
#     # Start checking for authentication status
#     root.after(1000, check_auth_status)

# # initialize the main window
# root = CTk()
# root.title("ECHOES")
# root.resizable(False, False)
# root.geometry("600x480")
# root.iconbitmap("icon.ico")

# # set the widgets, labels, text, etc
# logo_label = CTkLabel(root, image=logo_ctk, text="")
# logo_label.pack(pady=75)

# welcome = CTkLabel(root,
#                     text="Welcome!", 
#                     text_color="white",
#                     font=("Coolvetica", 40)
#                    )
# welcome.pack(pady=0)

# request = CTkLabel(root,
#                     text="Please login to continue", 
#                     text_color="white",
#                     font=("Helvetica", 20)
#                    )
# request.pack(pady=0)

# login_button = CTkButton(root,
#                     text="Login", 
#                     command=open_login_page,  # Connect to our new function
#                     height=50,
#                     width=512,
#                     corner_radius=32,
#                     font=("Coolvetica", 20)
# )
# login_button.pack(pady=25)

# # main loop
# if __name__ == "__main__":
#     root.mainloop()