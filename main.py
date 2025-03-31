"""
CSC111 Project 2: Spotify Recommendation System - GUI Module
This module handles the login, user data page, recomendations page and OAuth authentication.
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
        self.song_based_recomendations = self.tabview.add("Song-based Recommendations")
        self.user_based_recomendations = self.tabview.add("User-based Recommendations")
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

    def create_song_based_recommendation_tab(self):
        """Create song based recommendation tab UI"""
        # TODO: create input field for song name
        self.song_based_recomendations_label = CTkLabel(
            self.song_based_recomendations, 
            text="Please login to view this page.", 
            text_color="white", 
            font=("Coolvetica", 40),
            fg_color="#2FA572",
            corner_radius=20
            )
        self.song_based_recomendations_label.pack(pady=10)
    
    def create_user_based_recommendation_tab(self):
        """Create user-based recommendation tab UI"""
        self.user_based_recommendations_label = CTkLabel(
            self.user_based_recomendations, 
            text="Please login to view this page.", 
            text_color="white", 
            font=("Coolvetica", 40),
            fg_color="#2FA572",
            corner_radius=20
            )
        self.user_based_recommendations_label.pack(pady=10)

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
            
            # clear any existing widgets in the user_data_tab
            for widget in self.user_data_tab.winfo_children():
                widget.destroy()
                
            # update user_data_label with new text
            self.user_data_label = CTkLabel(
                master=self.user_data_tab,
                text="Your listening data in the past 6 months",
                font=("Coolvetica", 25),
                fg_color="#2FA572",
                text_color="white",
                corner_radius=20
            )
            self.user_data_label.pack(pady=(10, 5))
            
            # main frame
            main_frame = CTkScrollableFrame(
                master=self.user_data_tab,
                width=540,
                height=400,
                corner_radius=10,
                fg_color="transparent",
                border_color="#535454",
                border_width=2
            )
            main_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            # songs frame
            songs_frame = CTkFrame(
                master=main_frame,
                width=520,
                height=190,
                corner_radius=20,
                fg_color="#93D67C"
            )
            songs_frame.pack(fill="x", padx=5, pady=5)
            songs_frame.pack_propagate(False)
            
            # artists frame
            artists_frame = CTkFrame(
                master=main_frame,
                width=520,
                height=190,
                corner_radius=20,
                fg_color="#FF82FF"
            )
            artists_frame.pack(fill="x", padx=5, pady=5)
            artists_frame.pack_propagate(False)
            
            # labels
            tracks_label = CTkLabel(
                master=songs_frame,
                text=tracks_text if tracks else "No Songs Found",
                text_color="#535454",
                font=("Coolvetica", 25),
                fg_color=None,
                justify="center",
                anchor="center"
            )
            tracks_label.pack(fill="both", padx= 10,pady=10)
            
            artists_label = CTkLabel(
                master=artists_frame,
                text=artists_text if artists else "No Artists Found",
                text_color="#535454",
                font=("Coolvetica", 25),
                fg_color=None,
                justify="center",
                anchor="center"
            )
            artists_label.pack(fill="both", pady=10)
            
            # force update
            self.update()
            
        except Exception as e:
            self.user_data_label.configure(text=f"Error fetching data: {str(e)}\nPlease try again later.")

    def fetch_song_recommendations(self):
        """Fetch song-based recommendations from Spotify API"""
        if not self.authenticated or self.sp is None:
            self.song_based_recomendations_label.configure(text="User not authenticated. Please login.")
            return
        try:
            self.song_based_recomendations_label.configure(text="Please enter a song name below.")
            self.update()

        except Exception as e:
            self.song_based_recomendations_label.configure(text=f"Error fetching recommendations: {str(e)}\nPlease try again later.")

    def fetch_user_recommendations(self):
        """Fetch user-based recommendations from Spotify API"""
        if not self.authenticated or self.sp is None:
            self.user_based_recomendations_label.configure(text="User not authenticated. Please login.")
            return
        try:
            self.user_based_recommendations_label.configure(text="Finding your echoes...")
            self.update()

            # clear any existing widgets in the user_based_recomendations tab
            for widget in self.user_based_recomendations.winfo_children():
                widget.destroy()

            # update user_based_recomendations_label with new text
            self.user_based_recomendations_label = CTkLabel(
                master=self.user_based_recomendations,
                text="Your Echoes",
                font=("Coolvetica", 25),
                fg_color="#2FA572",
                text_color="white",
                corner_radius=20
            )
            self.user_based_recomendations_label.pack(pady=(10, 5))
            subtitle = CTkLabel(
                master=self.user_based_recomendations,
                text="Based on your listening habits",
                font=("Helvetica", 20),
                text_color="white"
            )
            subtitle.pack(pady=(0, 10))

            # main frame
            main_frame = CTkScrollableFrame(
                master=self.user_based_recomendations,
                width=540,
                height=400,
                corner_radius=10,
                fg_color="transparent",
                border_color="#535454",
                border_width=2
            )
            main_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # generate more button TODO: complete command
            generate_more_button = CTkButton(
                master=main_frame,
                text="Give me more suggestions",
                command=self.fetch_user_recommendations,
                fg_color="#9E1FFF",
                hover_color="#535454",
                height=40,
                width=250,
                corner_radius=32,
                font=("Coolvetica", 23)
            )
            generate_more_button.pack(pady=5)

            # most similar recommendations frame
            most_similar_frame = CTkScrollableFrame(
                master=main_frame,
                width=520,
                height=190,
                corner_radius=20,
                fg_color="#FF82FF"
            )
            most_similar_frame.pack(fill="x", padx=5, pady=5)
            most_similar_frame.pack_propagate(False)

            # you may also like frame
            you_may_also_like_frame = CTkScrollableFrame(
                master=main_frame,
                width=520,
                height=190,
                corner_radius=20,
                fg_color="#93D67C"
            )
            you_may_also_like_frame.pack(fill="x", padx=5, pady=5)
            you_may_also_like_frame.pack_propagate(False)

            # labels TODO: complete commands (text) for both labels
            most_similar_label = CTkLabel(
                master=most_similar_frame,
                text="Most Similar Recommendations",
                text_color="#535454",
                font=("Coolvetica", 25),
                fg_color=None,
                justify="center",
                anchor="center"
            )
            most_similar_label.pack(fill="both", padx=10, pady=10)

            you_may_also_like_lavel = CTkLabel(
                master=you_may_also_like_frame,
                text="You May Also Like",
                text_color="#535454",
                font=("Coolvetica", 25),
                fg_color=None,
                justify="center",
                anchor="center"
            )
            you_may_also_like_lavel.pack(fill="both", pady=10)

            # force update
            self.update()

        except Exception as e:
            self.user_based_recomendations_label.configure(text=f"Error fetching recommendations: {str(e)}\nPlease try again later.")

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
                self.login_button.configure(text="Logged in.", state="disabled")
                self.request_label.configure(text="Authentication was successful!")
                self.fetch_user_data()
                self.switch_to_user_based_recommendations()
                return
            
            # not authenticated yet, check again after a delay
            self.after(2000, lambda: self.check_auth_status(attempts + 1, max_attempts))
            
        except Exception as e:  # TODO: check efficiency of this
            # handle any exceptions during authentication check
            print(f"Auth check error: {str(e)}")
            self.after(2000, lambda: self.check_auth_status(attempts + 1, max_attempts))

    def switch_to_user_based_recommendations(self):
        """Switch to the user-based recommendations tab and fetch data"""
        if self.authenticated:
            self.tabview.set("User-based Recommendations")
            self.fetch_user_recommendations()
        else:
            self.tabview.set("Login")
            self.request_label.configure(text="Please login to continue.")

# main loop, runs the actual desktop application
if __name__ == "__main__":

    app = ECHOESgui()
    app.mainloop()