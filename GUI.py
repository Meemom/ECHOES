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
        self.authenticated = False

        # create tabview so it can handle multiple pages
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        # create tabs
        self.login_tab = self.tabview.add("Login")
        self.song_based_reccomendations = self.tabview.add("Song-based Recommendations")
        self.user_based_reccomendations = self.tabview.add("User-based Recommendations")
        self.user_data_tab = self.tabview.add("User Data")
        self.tabview.set("Login")

        self.create_login_tab()
        self.create_song_based_recommendation_tab()
        self.create_user_based_recommendation_tab()
        self.create_user_data_tab()
    
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

    def create_song_based_recommendation_tab(self):   # requires an input
        """Create song based recommendation tab UI"""
        # TODO: create input field for song name
        label = CTkLabel(
            self.song_based_reccomendations, 
            text="Please login to view this page.", 
            text_color="white", 
            font=("Coolvetica", 40),
            fg_color="#2FA572",
            corner_radius=20
            )
        label.pack(pady=165)
    
    def create_user_based_recommendation_tab(self):  # doesnt require an input
        """Create user-based recommendation tab UI"""
        label = CTkLabel(
            self.user_based_reccomendations, 
            text="Please login to view this page.", 
            text_color="white", 
            font=("Coolvetica", 40),
            fg_color="#2FA572",
            corner_radius=20
            )
        label.pack(pady=165)

    def create_user_data_tab(self):
        """Create user data tab UI"""
        self.user_data_label = CTkLabel(
            self.user_data_tab,
            text="Please login to view this page.",
            text_color="white",
            font=("Coolvetica", 40),
            fg_color="#2FA572",
            corner_radius=20
            )
        self.user_data_label.pack(pady=10)

    def fetch_user_data(self):
        """Fetch user data from Spotify API"""
        if not self.authenticated or self.sp is None:
            self.user.data_label.configure(text="User not authenticated. Please login.")
            return
        try:
            self.user_data_label.configure(text="Fetching your top tracks and artists...")
            self.update()
            top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='medium_term')
            top_artists = self.sp.current_user_top_artists(limit=5, time_range='medium_term')

            tracks = [track['name'] for track in top_tracks['items']]
            artists = [artist['name'] for artist in top_artists['items']]
            
            tracks_text = "Top 5 Songs:\n" + "\n".join(tracks) 
            artists_text = "Top 5 Artists:\n" + "\n".join(artists)
            
            main_frame = CTkScrollableFrame(
                master=self.user_data_tab,
                width=540,
                height=432,
                corner_radius=10, 
                fg_color="transparent",
                border_color="#535454",
                border_width=2
                )
            main_frame.pack_propagate(False)
            main_frame.pack(expand=True, fill="both", pady=0)

            songs_frame = CTkScrollableFrame(
                master=main_frame,
                width=530,
                height=210, 
                corner_radius=20,
                fg_color="#CDFF8B",

                )
            songs_frame.pack_propagate(False)
            songs_frame.pack(expand=True, fill="both", side="top", pady=0)

            artists_frame = CTkScrollableFrame(
                master=main_frame,
                width=530,
                height=210, 
                corner_radius=20,
                fg_color="#FF82FF"
                )
            artists_frame.pack_propagate(False)
            artists_frame.pack(side="top", fill="both", expand=True, pady=5)

            # Debugging visibility
            print("Songs Frame Created:", songs_frame)
            print("Artists Frame Created:", artists_frame)

            tracks_label = CTkLabel(
                master=songs_frame,
                text=tracks_text,
                text_color="black",
                font=("Coolvetica", 15),
                corner_radius=20
                )
            tracks_label.pack(expand=True, pady=0)

            artists_label = CTkLabel(
                master=artists_frame,
                text=artists_text,
                text_color="black",
                font=("Coolvetica", 15),
                corner_radius=20
                )
            artists_label.pack(expand=True, pady=5)
            self.update()
            self.user_data_label.configure(text="Your listening data in the past 6 months", font=("Coolvetica", 25))

        except Exception as e:
            self.user_data_label.configure(text=f"Error fetching data: {str(e)}\nPlease try again later.")

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
        
        # check authentication status periodically
        self.check_auth_status()

    def check_auth_status(self, attempts=0, max_attempts=5):
        """Check if authentication was successful"""
        if attempts >= max_attempts:
            # after several attempts, reset login button and show failure message
            self.login_button.configure(text="Login", state="normal")
            self.request_label.configure(text="Login timed out. Please try again.")
            return
        
        try:
            # try to create a SpotifyOAuth instance and get a valid token
            auth_manager = SpotifyOAuth(
                client_id=oauth.CLIENT_ID,
                client_secret=oauth.CLIENT_SECRET,
                redirect_uri=oauth.REDIRECT_URI,
                scope=oauth.SCOPE,
                cache_path=oauth.CACHE_PATH
            )
            
            token_info = auth_manager.get_cached_token()
            
            if token_info and not auth_manager.is_token_expired(token_info):
                # successfully authenticated
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                self.authenticated = True
                self.switch_to_user_based_recommendations()
                return
            
            # not authenticated yet, check again after a delay
            self.after(2000, lambda: self.check_auth_status(attempts + 1, max_attempts))
            
        except Exception as e:  # TODO: check efficiency of this
            # handle any exceptions during authentication check
            print(f"Auth check error: {str(e)}")
            self.after(2000, lambda: self.check_auth_status(attempts + 1, max_attempts))

    def switch_to_song_recommendations(self):
        """Switch to the recommendations tab after login"""
        if self.authenticated:
            self.tabview.set("Song-based Recommendations")
            self.login_button.configure(text="Logged in.", state="disabled")
            self.request_label.configure(text="Authentication was successful!")

    def switch_to_user_based_recommendations(self):
        """Switch to the user-based recommendations tab and fetch data"""
        if self.authenticated:
            self.tabview.set("User-based Recommendations")
            self.fetch_user_data()
        else:
            self.tabview.set("Login")
            self.request_label.configure(text="Please login to continue.")
    
    def switch_to_user_data(self):
        """Switch to the user data tab and fetch user data"""
        if self.authenticated:
            self.tabview.set("User Data")
            self.fetch_user_data()
        else:
            self.tabview.set("Login")
            self.request_label.configure(text="Please login to continue.")

# main loop, runs the actual desktop application
if __name__ == "__main__":
    app = ECHOESgui()
    app.mainloop()