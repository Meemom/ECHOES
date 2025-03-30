"""
CSC111 Project 2: Spotify Recommendation System - GUI Module
This module handles the login, user data page, reccomendations page and OAuth authentication.
"""

import tkinter as tk
from customtkinter import *
from PIL import Image
import spotipy
import threading
import webbrowser
import oauth_activation as oauth
from flask import Flask
from spotipy import SpotifyOAuth

# logo image files
icon = Image.open("images/icon.png")
icon.save("images/icon.ico", format="ICO")
logo = Image.open("images/logo.png")
logo_ctk = CTkImage(light_image=logo, size=(512,125))

# setting theme and appearance
set_appearance_mode("dark")
set_default_color_theme("green")

class ECHOESgui(CTk):
    """
    This class handles the GUI for the ECHOES application.
    """
    def __init__(self):
        # initialize the GUI
        super().__init__()

        self.title("ECHOES")
        self.geometry("600x480")
        self.resizable(False, False)
        self.iconbitmap("images/icon.ico")

        # initialize spotipy client
        self.sp = None
        self.authenticated = None

        # create tabview so it can handle multiple pages
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        # create tabs
        self.login_tab = self.tabview.add("Login")
        self.recommendation_tab = self.tabview.add("Recommendations")
        self.user_data_tab = self.tabview.add("User Data")
        self.tabview.set("Login")

        self.create_login_tab()
        self.create_recommendation_tab()
        self.create_user_data_tab()

        self.fetch_user_data()
    
    def create_login_tab(self):
        """Create login tab UI"""
        logo_label = CTkLabel(
            self.login_tab, 
            image=logo_ctk, 
            text=""
            )
        logo_label.pack(pady=75)

        welcome_label = CTkLabel(
            self.login_tab, 
            text="Welcome!", 
            text_color="white", 
            font=("Coolvetica", 40)
            )
        welcome_label.pack(pady=0)

        self.request_label = CTkLabel(
            self.login_tab, 
            text="Please login to continue", 
            text_color="white", 
            font=("Helvetica", 20))
        self.request_label.pack(pady=0)

        self.login_button = CTkButton(
            self.login_tab, 
            text="Login", 
            command=self.open_login_page, 
            height=50, 
            width=512, 
            corner_radius=32, 
            font=("Coolvetica", 20)
            )
        self.login_button.pack(pady=25)

    def create_recommendation_tab(self):
        """Create song recommendation tab UI"""
        label = CTkLabel(
            self.recommendation_tab, 
            text="Your Song Recommendations", 
            text_color="white", 
            font=("Helvetica", 20)
            )
        label.pack(pady=20)

    def create_user_data_tab(self):
        """Create user data tab UI"""
        self.user_data_label = CTkLabel(
            self.user_data_tab,
            text="Fetching user data...",
            text_color="white",
            font=("Helvetica", 20)
            )
        self.user_data_label.pack(pady=20)

    def fetch_user_data(self):
        """Fetch user data from Spotify API"""
        try:
            top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='medium_term')
            top_artists = self.sp.__annotations__current_user_top_artists(limit=5, time_range='medium_term')

            tracks = [track['name'] for track in top_tracks['items']]
            artists = [artist['name'] for artist in top_artists['items']]
        except:
            data_text = "Top 5 Songs:\n" + "\n".join(tracks) + "\n\nTop 5 Artists:\n" + "\n".join(artists)
        self.user_data_label.configure(text=data_text)

    def start_oauth_server(self):
        """Start the Flask server for OAuth in a separate thread"""
        oauth.app.run(debug=False)

    def open_login_page(self):
        """Open the Spotify login page and switch tabs on success"""
        server_thread = threading.Thread(
            target=self.start_oauth_server, 
            daemon=True
            )
        server_thread.start()

        authenticator = oauth.SpotifyAuthentication(
            oauth.CLIENT_ID, 
            oauth.CLIENT_SECRET, 
            oauth.REDIRECT_URI, 
            oauth.SCOPE
            )
        authenticator.setup_auth_manager()
        auth_url = authenticator.get_auth_url()
        webbrowser.open(auth_url)

        self.login_button.configure(text="Logging in...", state="disabled")
        self.request_label.configure(text="Authorization in progress. Please check your browser.")
        
        self.after(5000, self.setup_spotify)  # simulating login success

    def setup_spotify(self):
        """Initialize Spotipy client and handle login verification"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=oauth.CLIENT_ID,
                                                                client_secret=oauth.CLIENT_SECRET,
                                                                redirect_uri=oauth.REDIRECT_URI,
                                                                scope=oauth.SCOPE))
            self.authenticated = True
            self.switch_to_recommendations()
        except:
            self.request_label.configure(text="Login failed. Please try again.")
            self.login_button.configure(text="Login", state="normal")

    def switch_to_recommendations(self):
        """Switch to the recommendations tab after login"""
        if self.authenticated:
            self.tabview.set("Recommendations")
    
    def switch_to_user_data(self):
        """Switch to the user data tab and fetch user data"""
        if self.authenticated:
            self.tabview.set("User Data")
            self.fetch_user_data()


# main loop, runs the actual desktop application
if __name__ == "__main__":
    app = ECHOESgui()
    app.mainloop()