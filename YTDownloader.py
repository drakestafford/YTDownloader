import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import yt_dlp
from yt_dlp import YoutubeDL
import subprocess


def on_progress(stream, chunk, bytes_remaining):
    """Update progress bar based on download progress."""
    if stream.filesize == 0:
        return
    percent = (stream.filesize - bytes_remaining) / stream.filesize * 100
    progress_bar['value'] = percent
    root.update_idletasks()

def fetch_formats():
    """Fetch available video formats for the provided URL using yt-dlp."""
    url = url_entry.get().strip()
    try:
        ydl = YoutubeDL({'quiet': True, 'skip_download': True})
        info = ydl.extract_info(url, download=False)
        mp4_formats = [
            f for f in info['formats']
            if f.get('ext') == 'mp4' and f.get('vcodec') != 'none'
        ]
        stream_list.clear()
        stream_list.extend(mp4_formats)
        resolution_combo['values'] = [
            f.get('format_note') or f['height'] for f in mp4_formats
        ]
        resolution_combo.current(0)
    except Exception as e:
        print(f"Failed to fetch video formats: {e}")
        messagebox.showerror(
            "Error",
            "This video might be private, restricted, region-locked, or unsupported. Try a different one."
        )

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return
    directory = filedialog.askdirectory()
    if not directory:
        return
    # Build yt-dlp command: best MP4 video + best M4A audio, merge into MP4
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        "--merge-output-format", "mp4",
        "-o", f"{directory}/%(title)s.%(ext)s",
        url,
    ]
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", "Download completed!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"yt-dlp failed: {e}")

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
fetch_button = tk.Button(root, text="Fetch Streams", command=fetch_formats)
fetch_button.pack(side=tk.LEFT, padx=(50,20), pady=10)

download_button = tk.Button(root, text="Download Video", command=download_video)
download_button.pack(side=tk.RIGHT, padx=(20,50), pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=(0,10))

# Start the GUI event loop
root.mainloop()