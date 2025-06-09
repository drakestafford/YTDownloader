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
root.iconphoto(False, tk.PhotoImage(file="ds.icns"))
root.option_add("*Font", ("Helvetica", 12))
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