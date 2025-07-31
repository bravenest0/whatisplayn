import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext # For displaying recommendations

# --- Your Spotify App Credentials (REPLACE THESE!) ---
CLIENT_ID = 'a59de0fde8cc44d6ae088e8a22bd9695' # <-- Your Client ID goes here
CLIENT_SECRET = '5f0a7079257746da9855fcb25e017a0d' # <-- Your Client Secret goes here
REDIRECT_URI = 'http://127.0.0.1:8888/callback' # <-- Make sure this matches your Spotify app settings exactly
# ---------------------------------------------------

# Updated scope for controlling playback and reading user top items!
scope = "user-read-playback-state user-modify-playback-state user-top-read"

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
        master.geometry("400x550") # Increased window size for recommendations
        master.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TCheckbutton", font=("Arial", 10))

        # Initialize Spotify client as an instance attribute
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=scope
            ))
            print("Spotify client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Spotify: {e}")
            print("Please ensure your Client ID, Client Secret, and Redirect URI are correct.")
            print("Also, delete any .cache- files if you're stuck in an auth loop.")
            master.destroy()
            return

        # --- Current Playback Display ---
        self.playback_frame = ttk.Frame(master, borderwidth=2, relief="groove")
        self.playback_frame.pack(pady=10, padx=10, fill="x")

        self.title_label = ttk.Label(self.playback_frame, text="Loading...", style="Header.TLabel", wraplength=380)
        self.title_label.pack(pady=5)

        self.artist_label = ttk.Label(self.playback_frame, text="", wraplength=380)
        self.artist_label.pack(pady=2)

        self.album_label = ttk.Label(self.playback_frame, text="", wraplength=380)
        self.album_label.pack(pady=2)

        self.device_label = ttk.Label(self.playback_frame, text="", wraplength=380)
        self.device_label.pack(pady=2)

        self.time_label = ttk.Label(self.playback_frame, text="")
        self.time_label.pack(pady=5)

        self.status_label = ttk.Label(master, text="Waiting for playback...", style="TLabel")
        self.status_label.pack(pady=5)

        # --- Playback Control Buttons ---
        self.control_frame = ttk.Frame(master)
        self.control_frame.pack(pady=5)

        self.pause_button = ttk.Button(self.control_frame, text="Pause", command=self.pause_track)
        self.pause_button.grid(row=0, column=0, padx=5)

        self.play_button = ttk.Button(self.control_frame, text="Play", command=self.play_track)
        self.play_button.grid(row=0, column=1, padx=5)

        self.next_button = ttk.Button(self.control_frame, text="Next", command=self.skip_next)
        self.next_button.grid(row=0, column=2, padx=5)

        self.prev_button = ttk.Button(self.control_frame, text="Previous", command=self.skip_previous)
        self.prev_button.grid(row=0, column=3, padx=5)

        # --- Similar Songs Section ---
        self.recommendations_toggle_var = tk.BooleanVar()
        self.recommendations_toggle_var.set(False) # Default to off

        self.recommendations_checkbutton = ttk.Checkbutton(
            master,
            text="Show Similar Songs",
            variable=self.recommendations_toggle_var,
            command=self.toggle_recommendations,
            style="TCheckbutton"
        )
        self.recommendations_checkbutton.pack(pady=10)

        self.recommendations_frame = ttk.Frame(master, borderwidth=2, relief="groove")
        # Don't pack it initially, will pack when toggled on
        self.recommendations_label = ttk.Label(self.recommendations_frame, text="Similar Songs:", style="Header.TLabel")
        self.recommendations_display = scrolledtext.ScrolledText(self.recommendations_frame, width=40, height=8, wrap=tk.WORD, font=("Arial", 10))
        self.recommendations_display.insert(tk.END, "Enable 'Show Similar Songs' to see recommendations.\n")
        self.recommendations_display.config(state=tk.DISABLED) # Make it read-only

        # Start updating the display
        self.update_playback()


    # --- Playback Control Methods ---
    def pause_track(self):
        """Pauses the current Spotify playback."""
        try:
            self.sp.pause_playback()
            self.status_label.config(text="Playback Paused!")
            print("Playback paused via API.")
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error pausing playback: {e}")
            self.status_label.config(text="Error pausing. Check terminal.")
        except Exception as e:
            print(f"An unexpected error occurred during pause: {e}")
            self.status_label.config(text=f"Error: {e}")
        self.master.after(100, self.update_playback)

    def play_track(self):
        """Resumes/Starts Spotify playback."""
        try:
            self.sp.start_playback()
            self.status_label.config(text="Playback Resumed!")
            print("Playback resumed via API.")
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error resuming playback: {e}")
            self.status_label.config(text="Error resuming. Check terminal.")
        except Exception as e:
            print(f"An unexpected error occurred during play: {e}")
            self.status_label.config(text=f"Error: {e}")
        self.master.after(100, self.update_playback)

    def skip_next(self):
        """Skips to the next track."""
        try:
            self.sp.next_track()
            self.status_label.config(text="Skipping to next track...")
            print("Skipping to next track via API.")
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error skipping track: {e}")
            self.status_label.config(text="Error skipping. Check terminal.")
        except Exception as e:
            print(f"An unexpected error occurred during skip next: {e}")
            self.status_label.config(text=f"Error: {e}")
        self.master.after(100, self.update_playback)

    def skip_previous(self):
        """Skips to the previous track."""
        try:
            self.sp.previous_track()
            self.status_label.config(text="Skipping to previous track...")
            print("Skipping to previous track via API.")
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error skipping track: {e}")
            self.status_label.config(text="Error skipping. Check terminal.")
        except Exception as e:
            print(f"An unexpected error occurred during skip previous: {e}")
            self.status_label.config(text=f"Error: {e}")
        self.master.after(100, self.update_playback)


    # --- Recommendation Methods ---
    def toggle_recommendations(self):
        """Shows or hides the recommendations frame."""
        if self.recommendations_toggle_var.get():
            self.recommendations_frame.pack(pady=10, padx=10, fill="both", expand=True)
            self.recommendations_label.pack(pady=5)
            self.recommendations_display.pack(fill="both", expand=True)
            self.get_and_display_recommendations() # Fetch immediately when toggled on
        else:
            self.recommendations_frame.pack_forget()

    def get_and_display_recommendations(self):
        """Fetches and displays similar songs based on the current track/artist."""
        self.recommendations_display.config(state=tk.NORMAL) # Enable editing
        self.recommendations_display.delete(1.0, tk.END) # Clear previous recommendations
        self.recommendations_display.insert(tk.END, "Fetching recommendations...\n")
        self.recommendations_display.config(state=tk.DISABLED) # Disable editing

        try:
            current = self.sp.current_playback()
            seed_artists = []
            seed_tracks = []
            seed_genres = [] # Spotify also supports genre seeds, but we won't use it directly from current track

            if current and current['is_playing']:
                track = current['item']
                for artist in track['artists']:
                    seed_artists.append(artist['id'])
                seed_tracks.append(track['id'])

            # Fallback: If no current track, try to get user's top artists/tracks as seeds
            if not seed_artists and not seed_tracks:
                print("No current playback to seed recommendations. Trying user's top artists/tracks...")
                top_artists = self.sp.current_user_top_artists(limit=3)['items']
                for artist in top_artists:
                    seed_artists.append(artist['id'])
                top_tracks = self.sp.current_user_top_tracks(limit=2)['items']
                for track in top_tracks:
                    seed_tracks.append(track['id'])

            if seed_artists or seed_tracks:
                # Limit seeds to 5 total, as per Spotify API recommendations endpoint
                recommendations = self.sp.recommendations(
                    seed_artists=seed_artists[:5],
                    seed_tracks=seed_tracks[:5],
                    limit=10 # Get 10 recommended tracks
                )

                if recommendations and recommendations['tracks']:
                    self.recommendations_display.config(state=tk.NORMAL)
                    self.recommendations_display.delete(1.0, tk.END) # Clear loading message
                    self.recommendations_display.insert(tk.END, "Recommended Tracks:\n")
                    for i, track in enumerate(recommendations['tracks']):
                        artists = ", ".join([artist['name'] for artist in track['artists']])
                        self.recommendations_display.insert(tk.END, f"{i+1}. {track['name']} - {artists}\n")
                    self.recommendations_display.config(state=tk.DISABLED)
                else:
                    self.recommendations_display.config(state=tk.NORMAL)
                    self.recommendations_display.delete(1.0, tk.END)
                    self.recommendations_display.insert(tk.END, "No recommendations found based on current context.\n")
                    self.recommendations_display.config(state=tk.DISABLED)
            else:
                self.recommendations_display.config(state=tk.NORMAL)
                self.recommendations_display.delete(1.0, tk.END)
                self.recommendations_display.insert(tk.END, "Could not generate recommendations (no active track or top user data).\n")
                self.recommendations_display.config(state=tk.DISABLED)

        except spotipy.exceptions.SpotifyException as e:
            error_message = f"Spotify API Error fetching recommendations: {e}"
            print(error_message)
            self.recommendations_display.config(state=tk.NORMAL)
            self.recommendations_display.delete(1.0, tk.END)
            self.recommendations_display.insert(tk.END, f"Error fetching recommendations: {e}\n")
            self.recommendations_display.config(state=tk.DISABLED)
            # This might happen if the token expired. Re-auth logic is in update_playback
        except Exception as e:
            error_message = f"An unexpected error occurred while getting recommendations: {e}"
            print(error_message)
            self.recommendations_display.config(state=tk.NORMAL)
            self.recommendations_display.delete(1.0, tk.END)
            self.recommendations_display.insert(tk.END, f"Unexpected error: {e}\n")
            self.recommendations_display.config(state=tk.DISABLED)

    def update_playback(self):
        """Fetches and updates the Spotify playback information."""
        try:
            current = self.sp.current_playback()

            if current:
                if current['is_playing']:
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
                    self.pause_button.config(state="normal")
                    self.play_button.config(state="disabled")
                    self.next_button.config(state="normal")
                    self.prev_button.config(state="normal")

                    # If recommendations are toggled on, update them here
                    if self.recommendations_toggle_var.get():
                        self.get_and_display_recommendations()
                else:
                    self.title_label.config(text="Playback Paused / Inactive")
                    if current and 'item' in current and current['item']:
                        track = current['item']
                        self.artist_label.config(text=f"Artist(s): {', '.join([artist['name'] for artist in track['artists']])}")
                        self.album_label.config(text=f"Album: {track['album']['name']}")
                        self.time_label.config(text=f"{format_time(current.get('progress_ms', 0))} / {format_time(track.get('duration_ms', 0))}")
                    else:
                        self.artist_label.config(text="")
                        self.album_label.config(text="")
                        self.time_label.config(text="")

                    if current and 'device' in current and current['device']:
                        device = current['device']
                        self.device_label.config(text=f"Device: {device['name']} ({device['type']})")
                    else:
                        self.device_label.config(text="")

                    self.status_label.config(text="Waiting for playback...")
                    self.pause_button.config(state="disabled")
                    self.play_button.config(state="normal")
                    self.next_button.config(state="disabled")
                    self.prev_button.config(state="disabled")

                    # If recommendations are toggled on, update them (might be based on last played)
                    if self.recommendations_toggle_var.get():
                        self.get_and_display_recommendations()

            else:
                self.title_label.config(text="No active Spotify device or playback")
                self.artist_label.config(text="")
                self.album_label.config(text="")
                self.device_label.config(text="")
                self.time_label.config(text="")
                self.status_label.config(text="Waiting for playback...")
                self.pause_button.config(state="disabled")
                self.play_button.config(state="disabled")
                self.next_button.config(state="disabled")
                self.prev_button.config(state="disabled")

                # Clear recommendations if no active playback
                if self.recommendations_toggle_var.get():
                    self.recommendations_display.config(state=tk.NORMAL)
                    self.recommendations_display.delete(1.0, tk.END)
                    self.recommendations_display.insert(tk.END, "No active playback to generate recommendations from.\n")
                    self.recommendations_display.config(state=tk.DISABLED)


        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API Error: {e}")
            self.status_label.config(text="Spotify Error. Check terminal for details. Attempting re-auth...")
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    redirect_uri=REDIRECT_URI,
                    scope=scope
                ))
                print("Re-authentication successful.")
                self.status_label.config(text="Re-authenticated. Retrying...")
            except Exception as auth_e:
                self.status_label.config(text=f"Auth Failed: {auth_e}")
                print(f"Failed to re-authenticate: {auth_e}")
                return

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.status_label.config(text=f"Error: {e}")

        self.master.after(5000, self.update_playback)

# Main part of the script
if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyMonitorApp(root)
    root.mainloop()