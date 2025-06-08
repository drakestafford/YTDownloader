import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pytube import YouTube
import yt_dlp


def on_progress(stream, chunk, bytes_remaining):
    """Update progress bar based on download progress."""
    if stream.filesize == 0:
        return
    percent = (stream.filesize - bytes_remaining) / stream.filesize * 100
    progress_bar['value'] = percent
    root.update_idletasks()

yt = None


def fetch_streams():
    """Fetch available streams for the provided URL."""
    global yt
    url = url_entry.get().strip()
    sanitized_url = url.split("&")[0]
    try:
        yt = YouTube(sanitized_url, on_progress_callback=on_progress)
        streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        stream_list.clear()
        for stream in streams:
            stream_list.append(stream)
        resolution_combo['values'] = [stream.resolution for stream in streams]
        resolution_combo.current(0)
    except Exception as e:
        # Log the real error to the terminal for debugging purposes
        print(f"Failed to fetch video streams: {e}")
        # Show a user-friendly message in the popup dialog
        messagebox.showerror(
            "Error",
            "This video might be private, restricted, region-locked, or unsupported. Try a different one."
        )

def download_video():
    directory = filedialog.askdirectory()
    if directory:
        progress_bar['value'] = 0
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
            'noprogress': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_entry.get().strip().split('&')[0]])
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")

# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("600x230")  # Width x Height

stream_list = []

# URL entry
url_label = tk.Label(root, text="Enter YouTube URL:")
url_label.pack(padx=10, pady=(10,0))
url_entry = tk.Entry(root, width=60, bg='white', fg='dark blue', borderwidth=2, relief="groove")
url_entry.pack(padx=10, pady=(0,10))

# Resolution dropdown
resolution_label = tk.Label(root, text="Select Resolution:")
resolution_label.pack(padx=10, pady=(10,0))
resolution_combo = ttk.Combobox(root, state="readonly", width=58)
resolution_combo.pack(padx=10, pady=(0,10))

# Fetch streams and download buttons
fetch_button = tk.Button(root, text="Fetch Streams", command=fetch_streams)
fetch_button.pack(side=tk.LEFT, padx=(50,20), pady=10)

download_button = tk.Button(root, text="Download Video", command=download_video)
download_button.pack(side=tk.RIGHT, padx=(20,50), pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=(0,10))

# Start the GUI event loop
root.mainloop()
