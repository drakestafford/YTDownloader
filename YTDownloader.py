import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pytube import YouTube

def fetch_streams():
    url = url_entry.get()
    try:
        video = YouTube(url)
        streams = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        stream_list.clear()
        for stream in streams:
            stream_list.append(stream)
        resolution_combo['values'] = [stream.resolution for stream in streams]
        resolution_combo.current(0)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch video streams: {e}")

def download_video():
    selected_stream = stream_list[resolution_combo.current()]
    directory = filedialog.askdirectory()
    if directory:
        try:
            selected_stream.download(output_path=directory)
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")

# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("600x200")  # Width x Height

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

# Start the GUI event loop
root.mainloop()