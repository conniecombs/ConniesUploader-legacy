# modules/file_handler.py
import os
import threading
from PIL import Image, ImageTk
from . import config

def scan_inputs(inputs):
    """Returns list of (folder_name, [file_paths])."""
    jobs = [] # list of tuples
    misc_files = []

    for path in inputs:
        if os.path.isdir(path):
            folder_name = os.path.basename(path.rstrip(os.sep))
            files = []
            for root, _, names in os.walk(path):
                for n in names:
                    if n.lower().endswith(config.SUPPORTED_EXTENSIONS):
                        files.append(os.path.join(root, n))
            if files:
                jobs.append((folder_name, sorted(files, key=config.natural_sort_key)))
        elif path.lower().endswith(config.SUPPORTED_EXTENSIONS):
            misc_files.append(path)
    
    if misc_files:
        jobs.append(("Miscellaneous", sorted(misc_files, key=config.natural_sort_key)))
    
    return jobs

def start_thumbnail_generation(file_list, group_widget, ui_queue):
    """Runs in background thread to generate thumbnails."""
    def worker():
        for f in file_list:
            try:
                img = Image.open(f)
                img.thumbnail(config.UI_THUMB_SIZE)
                ph = ImageTk.PhotoImage(img)
            except:
                ph = None
            ui_queue.put(('add_row', f, ph, group_widget))
    threading.Thread(target=worker, daemon=True).start()