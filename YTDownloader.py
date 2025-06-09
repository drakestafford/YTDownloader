import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from yt_dlp import YoutubeDL


def on_progress(d):
    """Update progress bar based on yt-dlp download progress."""
    if d.get('status') == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total * 100
            progress_bar['value'] = percent
            root.update_idletasks()
    elif d.get('status') == 'finished':
        progress_bar['value'] = 100
        root.update_idletasks()

def fetch_formats():
    """Fetch available video formats for the provided URL using yt-dlp."""
    url = url_entry.get().strip()
    download_button.config(state=tk.DISABLED)
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
        if mp4_formats:
            resolution_combo.current(0)
            download_button.config(state=tk.NORMAL)
    except Exception as e:
        print(f"Failed to fetch video formats: {e}")
        messagebox.showerror(
            "Error",
            "This video might be private, restricted, region-locked, or unsupported. Try a different one."
        )
        download_button.config(state=tk.DISABLED)

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return
    directory = filedialog.askdirectory()
    if not directory:
        return
    progress_bar['value'] = 0
    root.update_idletasks()
    # yt-dlp options with progress hook
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
        'progress_hooks': [on_progress],
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror(
            "Download Failed",
            "Couldn\u2019t assemble an mp4+audio combo. "
            "Try a different video/resolution or install ffmpeg.\n" + str(e)
        )

# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")
# Keep the window compact but wide enough for inputs
root.geometry("500x220")  # Width x Height

# Ensure widgets expand nicely
root.columnconfigure(0, weight=1)

stream_list = []

# Frame for URL input
url_frame = ttk.Frame(root, padding=10)
url_frame.grid(row=0, column=0, sticky="ew")
url_frame.columnconfigure(1, weight=1)

url_label = ttk.Label(url_frame, text="Enter YouTube URL:")
url_label.grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
url_entry = ttk.Entry(url_frame, width=60)
url_entry.grid(row=0, column=1, padx=(0,5), pady=5, sticky="ew")

# Frame for resolution selection
resolution_frame = ttk.Frame(root, padding=10)
resolution_frame.grid(row=1, column=0, sticky="ew")
resolution_frame.columnconfigure(1, weight=1)

resolution_label = ttk.Label(resolution_frame, text="Select Resolution:")
resolution_label.grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
resolution_combo = ttk.Combobox(resolution_frame, state="readonly", width=58)
resolution_combo.grid(row=0, column=1, padx=(0,5), pady=5, sticky="ew")

# Frame for action buttons
button_frame = ttk.Frame(root, padding=10)
button_frame.grid(row=2, column=0, sticky="ew")
button_frame.columnconfigure((0,1), weight=1)

fetch_button = tk.Button(button_frame, text="Fetch Streams", command=fetch_formats)
fetch_button.grid(row=0, column=0, padx=5, pady=5, sticky="e")

download_button = tk.Button(button_frame, text="Download Video", command=download_video, state=tk.DISABLED)
download_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Progress bar
progress_frame = ttk.Frame(root, padding=(10,0,10,10))
progress_frame.grid(row=3, column=0, sticky="ew")

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
progress_bar.grid(row=0, column=0, sticky="ew")
progress_frame.columnconfigure(0, weight=1)

# Start the GUI event loop
root.mainloop()