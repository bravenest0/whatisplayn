# V 1.0.0
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import tkinter as tk
from tkinter import ttk # For potentially nicer looking widgets

# --- Your Spotify App Credentials (REPLACE THESE!) ---
# IMPORTANT: Replace these placeholders with your actual Client ID and Client Secret
CLIENT_ID = 'a59de0fde8cc44d6ae088e8a22bd9695' # <-- Your Client ID goes here
CLIENT_SECRET = '5f0a7079257746da9855fcb25e017a0d' # <-- Your Client Secret goes here
REDIRECT_URI = 'http://127.0.0.1:8888/callback' # <-- Make sure this matches your Spotify app settings exactly
# ---------------------------------------------------

scope = "user-read-playback-state"

def format_time(ms):
    """Converts milliseconds to human-readable M:SS format."""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

class SpotifyMonitorApp:
    def __init__(self, master):
        self.master = master
        master.title("Spotify Now Playing")
        master.geometry("400x250") # Set initial window size
        master.resizable(False, False) # Prevent resizing

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))

        # Initialize Spotify client as an instance attribute
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=scope
            ))
            print("Spotify client initialized successfully.") # For terminal debugging
        except Exception as e:
            # If initial auth fails, display error and exit.
            # User needs to fix credentials or delete cache before running.
            print(f"Error initializing Spotify: {e}")
            print("Please ensure your Client ID, Client Secret, and Redirect URI are correct.")
            print("Also, delete any .cache- files if you're stuck in an auth loop.")
            master.destroy() # Close the window if we can't even start Spotify
            return # Stop further initialization

        # Create labels to display information
        self.title_label = ttk.Label(master, text="Loading...", style="Header.TLabel", wraplength=380)
        self.title_label.pack(pady=5)

        self.artist_label = ttk.Label(master, text="", wraplength=380)
        self.artist_label.pack(pady=2)

        self.album_label = ttk.Label(master, text="", wraplength=380)
        self.album_label.pack(pady=2)

        self.device_label = ttk.Label(master, text="", wraplength=380)
        self.device_label.pack(pady=2)

        self.time_label = ttk.Label(master, text="")
        self.time_label.pack(pady=5)

        self.status_label = ttk.Label(master, text="Waiting for playback...", style="TLabel")
        self.status_label.pack(pady=10)

        # Start updating the display
        self.update_playback()

    def update_playback(self):
        """Fetches and updates the Spotify playback information."""
        try:
            # Use self.sp to access the Spotify client instance
            current = self.sp.current_playback()

            if current and current['is_playing']:
                track = current['item']
                device = current['device']
                progress_ms = current['progress_ms']
                duration_ms = track['duration_ms']

                time_elapsed = format_time(progress_ms)
                time_remaining = format_time(duration_ms - progress_ms)

                self.title_label.config(text=f"{track['name']}")
                self.artist_label.config(text=f"Artist(s): {', '.join([artist['name'] for artist in track['artists']])}")
                self.album_label.config(text=f"Album: {track['album']['name']}")
                self.device_label.config(text=f"Device: {device['name']} ({device['type']})")
                self.time_label.config(text=f"Time: {time_elapsed} / {format_time(duration_ms)} ({time_remaining} left)")
                self.status_label.config(text="Playing Now")

            else:
                self.title_label.config(text="No song playing")
                self.artist_label.config(text="")
                self.album_label.config(text="")
                self.device_label.config(text="")
                self.time_label.config(text="")
                self.status_label.config(text="Waiting for playback...")

        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API Error: {e}")
            self.status_label.config(text="Spotify Error. Check terminal for details. Attempting re-auth...")
            # If token expires, attempt to re-authenticate by re-initializing self.sp
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth( # Reassign self.sp
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    redirect_uri=REDIRECT_URI,
                    scope=scope
                ))
                print("Re-authentication successful.")
            except Exception as auth_e:
                self.status_label.config(text=f"Auth Failed: {auth_e}")
                print(f"Failed to re-authenticate: {auth_e}")
                # You might want to stop updates or destroy the window here if re-auth consistently fails
                return # Stop scheduling further updates if re-auth fails to prevent loop

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.status_label.config(text=f"Error: {e}")

        # Schedule the next update after 5000 milliseconds (5 seconds)
        self.master.after(1000, self.update_playback)

# Main part of the script
if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyMonitorApp(root)
    root.mainloop() # This starts the Tkinter event loop, keeping the window open
