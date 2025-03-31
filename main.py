"""
CSC111 Project 2: Spotify Recommendation System - GUI Module
This module handles the login, user data page, recommendations page and OAuth authentication.
"""
import python_ta
from customtkinter import *
from PIL import Image
import spotipy
import threading
import webbrowser
import oauth_activation as oauth
from spotipy import SpotifyOAuth
import recommender_graph_v2 as user_recs
import updated_decision_tree as song_recs
import pandas as pd
import os
import random
import sklearn


class ECHOESgui(CTk):
    """
    This class handles the GUI for the ECHOES application.
    """
    def __init__(self):
        # initialize the GUI
        super().__init__()

        # setting theme and appearance
        set_appearance_mode("dark")
        set_default_color_theme("green")

        # initialize the main window
        self.title("ECHOES")
        self.geometry("600x480")
        self.resizable(False, False)
        self.iconbitmap("images/icon.ico")

        # initialize spotipy client
        self.sp = None
        self.authenticated = False
        self.seen = {}

        # create tabview so it can handle multiple pages
        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        # create tabs
        self.login_tab = self.tabview.add("Login")
        self.song_based_recommendations = self.tabview.add("Song-based Recommendations")
        self.user_based_recommendations = self.tabview.add("User-based Recommendations")
        self.user_data_tab = self.tabview.add("User Data")
        self.tabview.set("Login")

        self.create_login_tab()
        self.create_song_based_recommendation_tab()
        self.create_user_based_recommendation_tab()
        self.create_user_data_tab()

        # clears cache after closing app
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # load decision tree model and dataset for song recommendations
        self.song_recommendation_dtree = None
        self.song_recommendation_features = ['speechiness', 'tempo', 'energy', 'loudness', 'acousticness',
                                             'danceability', 'instrumentalness']
        self.song_recommendation_dataset = None

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
            font=("Helvetica", 20)
        )
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
        self.chosen_song_label = CTkLabel(
            self.song_based_recommendations,
            text="Recommendations based on:",
            text_color="white",
            font=("Coolvetica", 20),
            bg_color="#2FA572",
            corner_radius=20
        )
        self.chosen_song_label.pack(pady=(10, 5))

        # label to display the chosen song name
        self.display_chosen_song_label = CTkLabel(
            self.song_based_recommendations,
            text="",
            text_color="#2FA572",
            font=("Helvetica", 18, "italic")
        )
        self.display_chosen_song_label.pack(pady=(0, 10))

        self.fetch_song_rec_button = CTkButton(
            self.song_based_recommendations,
            text="Get Song Recommendations",
            command=self.fetch_song_recommendations,
            height=40,
            width=250,
            corner_radius=32,
            fg_color="#9E1FFF",
            font=("Coolvetica", 18)
        )
        self.fetch_song_rec_button.pack(pady=(0, 20))

        self.song_based_recommendations_output_label = CTkLabel(  # Label to display messages or recommendations
            self.song_based_recommendations,
            text="",
            text_color="white",
            font=("Helvetica", 25),
            justify="center",
            anchor="center"
        )
        self.song_based_recommendations_output_label.pack(pady=(0, 10))

        self.song_recommendations_frame = CTkScrollableFrame(  # Frame to hold song recommendations
            self.song_based_recommendations,
            width=540,
            height=250,
            corner_radius=10,
            fg_color="transparent",
            border_color="#535454",
            border_width=2
        )
        self.song_recommendations_frame.pack(expand=True, fill="both", padx=10, pady=10)

    def create_user_based_recommendation_tab(self):
        """Create user-based recommendation tab UI"""
        self.user_based_recommendations_label = CTkLabel(
            self.user_based_recommendations,
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
            self.user_data_label.configure(text="User not authenticated. Please login.")
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
            tracks_label.pack(fill="both", padx=10, pady=10)

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
            self.song_based_recommendations_label.configure(text="User not authenticated. Please login.")
            return
        try:
            pass
        except Exception as e:
            self.song_based_recommendations.configure(text=f"Error fetching recommendations: "
                                                           f"{str(e)}\nPlease try again later.")

    def fetch_more_user_recommendations(self):
        """Fetch additional recommendations and update the label when a user presses the
        "Give me more suggestions" button."""
        try:
            graph = user_recs.load_song_listening_graph('datasets/spotify_dataset.csv', self.sp,
                                                        'datasets/user_song_data.csv')
            new_recommendations = graph.get_recommendations(seen=self.seen)

            # extract songs + artists then format
            new_recommendations_text = "\n".join(
                f"Song: {song}, Artist: {artist}"
                for item in new_recommendations if isinstance(item, tuple) for song, artist in [item]
            )

            if not new_recommendations_text:
                return  # if there exists no new recs, do nothing

            # append new recommendations to the existing label text
            current_text = self.most_similar_label.cget("text")
            updated_text = f"{current_text}\n{new_recommendations_text}"

            # update the suggestions label w/ the new suggestions
            self.most_similar_label.configure(text=updated_text)
            self.most_similar_label.update_idletasks()  # force ui update

        except Exception as e:
            print(f"Error loading more recommendations: {e}")  # print the error

    def fetch_user_recommendations(self):
        """Fetch user-based recommendations from Spotify API"""
        if not self.authenticated or self.sp is None:
            self.user.based_recommendations_label.configure(text="User not authenticated. Please login.")
            return
        try:
            self.user_based_recommendations_label.configure(text="Finding your echoes...")
            self.update()

            # clear any existing widgets in the user_based_recommendations tab
            for widget in self.user_based_recommendations.winfo_children():
                widget.destroy()

            graph = user_recs.load_song_listening_graph('datasets/spotify_dataset.csv', self.sp,
                                                        'datasets/user_song_data.csv')
            recommendations = graph.get_recommendations(seen=self.seen)
            recommendations_text = "\n".join(f"Song: {song}, Artist: {artist}" for item in recommendations if
                                             isinstance(item, tuple) for song, artist in [item])

            # update user_based_recommendations_label with new text
            self.user_based_recommendations_label = CTkLabel(
                master=self.user_based_recommendations,
                text="Your Echoes",
                font=("Coolvetica", 25),
                fg_color="#2FA572",
                text_color="white",
                corner_radius=20
            )
            self.user_based_recommendations_label.pack(pady=(10, 5))
            subtitle = CTkLabel(
                master=self.user_based_recommendations,
                text="Based on your listening habits...",
                font=("Helvetica", 20),
                text_color="white"
            )
            subtitle.pack(pady=(0, 10))

            # main frame
            main_frame = CTkScrollableFrame(
                master=self.user_based_recommendations,
                width=540,
                height=400,
                corner_radius=10,
                fg_color="transparent",
                border_color="#535454",
                border_width=2
            )
            main_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # most similar recommendations frame
            most_similar_frame = CTkScrollableFrame(
                master=main_frame,
                width=520,
                height=250,
                corner_radius=20,
                fg_color="#FF82FF",
                border_width=2,
                border_color="#535454"
            )
            most_similar_frame.pack(fill="x", padx=5, pady=5, expand=True)
            most_similar_frame.pack_propagate(True)

            title_label = CTkLabel(
                master=most_similar_frame,
                text="These are the songs that you might like",
                text_color="#93D67C",
                fg_color="#535454",
                corner_radius=20,
                font=("Coolvetica", 25, "italic"),
                justify="center",
                anchor="center"
            )
            title_label.pack(fill="both", padx=10, pady=10)

            self.most_similar_label = CTkLabel(
                master=most_similar_frame,
                height=200,
                text=recommendations_text,
                text_color="#535454",
                font=("Coolvetica", 20),
                justify="left",
                anchor="w",
                wraplength=480
            )
            self.most_similar_label.pack(fill="both", padx=10, pady=10, expand=True)

            # generate more suggestions button
            generate_more_button = CTkButton(
                master=main_frame,
                text="Give me more suggestions",
                command=self.fetch_more_user_recommendations,
                fg_color="#9E1FFF",
                hover_color="#535454",
                height=40,
                width=250,
                corner_radius=32,
                font=("Coolvetica", 23)
            )
            generate_more_button.pack(pady=5)

            # force update
            self.update()

        except Exception as e:
            self.user_based_recommendations_label.configure(text=f"Error fetching recommendations: "
                                                                 f"{str(e)}\nPlease try again later.")

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

    def switch_to_user_based_recommendations(self):
        """Switch to the user-based recommendations tab and fetch data"""
        if self.authenticated:
            self.tabview.set("User-based Recommendations")
            self.fetch_user_recommendations()
        else:
            self.tabview.set("Login")
            self.request_label.configure(text="Please login to continue.")

    def on_closing(self):
        """Clear cahce and close window so that authentication works properly each run iteration."""
        cache_path = oauth.CACHE_PATH
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                print(f"Cache file '{cache_path}' deleted.")
            except OSError as e:
                print(f"Error deleting cache file '{cache_path}': {e}")
        self.destroy()


# main loop, runs the actual desktop application
if __name__ == "__main__":
    # logo image files
    icon = Image.open("images/icon.png")
    icon.save("images/icon.ico", format="ICO")
    logo = Image.open("images/logo.png")
    logo_ctk = CTkImage(light_image=logo, size=(512, 125))

    app = ECHOESgui()
    app.mainloop()

    python_ta.check_all(config={
        'extra-imports': ["tkinter", "customtkinter", "PIL", "spotipy", "threading", "webbrowser",
                          "oauth_activation"],
        'max-line-length': 120
    })
