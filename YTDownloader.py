from ttkbootstrap import Window, ttk
from tkinter import filedialog, messagebox
import tkinter as tk
import threading
import os
from yt_dlp import YoutubeDL


def update_progress(percent, text):
    """Helper to update progress bar and label in the UI."""
    progress_bar['value'] = percent
    progress_label.config(text=text)
    root.update_idletasks()


def on_progress(d):
    """Update progress bar and label from yt-dlp progress hook."""
    if d.get('status') == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total * 100
            text = f"{downloaded/1048576:.1f}MB / {total/1048576:.1f}MB"
            root.after(0, update_progress, percent, text)
    elif d.get('status') == 'finished':
        root.after(0, update_progress, 100, "Completed")

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

    def run_download():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            root.after(0, lambda: messagebox.showinfo("Success", "Download completed!"))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror(
                "Download Failed",
                "Couldn\u2019t assemble an mp4+audio combo. "
                "Try a different video/resolution or install ffmpeg.\n" + str(e)
            ))

    threading.Thread(target=run_download, daemon=True).start()

# Create the main window with a built-in ttkbootstrap theme
# Use the "yeti" theme by default
root = Window(themename="yeti")
root.title("YouTube Downloader")
root.geometry("600x230")  # Width x Height

# Theme selection menu
menubar = tk.Menu(root)
theme_menu = tk.Menu(menubar, tearoff=False)
for theme in root.style.theme_names():
    theme_menu.add_command(label=theme, command=lambda t=theme: root.style.theme_use(t))
menubar.add_cascade(label="Themes", menu=theme_menu)
root.config(menu=menubar)

stream_list = []

# URL entry
url_label = ttk.Label(root, text="Enter YouTube URL:")
url_label.pack(padx=10, pady=(10,0))
url_entry = ttk.Entry(root, width=60)
url_entry.pack(padx=10, pady=(0,10))
url_menu = tk.Menu(root, tearoff=False)
url_menu.add_command(label="Paste", command=lambda: url_entry.event_generate("<<Paste>>"))
def show_menu(e):
    url_menu.tk_popup(e.x_root, e.y_root)
url_entry.bind("<Button-3>", show_menu)
url_entry.bind("<Control-Button-1>", show_menu)

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

# Progress bar and label
progress_label = ttk.Label(root, text="")
progress_label.pack(padx=10, pady=(0,5))
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=(0,10))

# Start the GUI event loop
root.mainloop()
