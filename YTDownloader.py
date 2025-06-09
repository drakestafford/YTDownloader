from ttkbootstrap import Window, ttk
from tkinter import filedialog, messagebox
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

def fetch_streams():
    """Fetch available video streams for the provided URL using yt-dlp."""
    url = url_entry.get().strip()
    try:
        ydl = YoutubeDL({'quiet': True, 'skip_download': True})
        info = ydl.extract_info(url, download=False)
        mp4_streams = [
            f for f in info['formats']
            if (
                f.get('ext') == 'mp4'
                and f.get('vcodec') != 'none'
            )
        ]

        # sort by resolution descending
        mp4_streams.sort(key=lambda f: f.get('height', 0), reverse=True)

        unique_map = {}
        for s in mp4_streams:
            res = s.get('height')
            if res and res not in unique_map:
                unique_map[res] = s

        resolutions = [f"{h}p" for h in unique_map.keys()]
        stream_list.clear()
        stream_list.extend(unique_map.values())
        resolution_combo['values'] = resolutions
        if resolutions:
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
    selected = stream_list[resolution_combo.current()] if stream_list else None
    if not selected:
        messagebox.showerror("Error", "Please fetch streams first.")
        return

    fmt = selected['format_id']
    if selected.get('acodec') == 'none':
        fmt = f"{fmt}+bestaudio[ext=m4a]/bestaudio"

    # yt-dlp options with progress hook for the chosen format
    ydl_opts = {
        'format': fmt,
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

# Create the main window with a built-in ttkbootstrap theme
root = Window(themename="flatly")
root.title("YouTube Downloader")
root.geometry("600x230")  # Width x Height

stream_list = []

# URL entry
url_label = ttk.Label(root, text="Enter YouTube URL:")
url_label.pack(padx=10, pady=(10,0))
url_entry = ttk.Entry(root, width=60)
url_entry.pack(padx=10, pady=(0,10))

# Resolution dropdown
resolution_label = ttk.Label(root, text="Select Resolution:")
resolution_label.pack(padx=10, pady=(10,0))
resolution_combo = ttk.Combobox(root, state="readonly", width=58)
resolution_combo.pack(padx=10, pady=(0,10))

# Fetch streams and download buttons
fetch_button = ttk.Button(root, text="Fetch Streams", command=fetch_streams)
fetch_button.pack(side="left", padx=(50,20), pady=10)

download_button = ttk.Button(root, text="Download Video", command=download_video)
download_button.pack(side="right", padx=(20,50), pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=(0,10))

# Start the GUI event loop
root.mainloop()
