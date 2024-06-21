from pathlib import Path

from PIL import Image

exts = Image.registered_extensions()
supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}


import os


def glob(directory):
    "Recursively find all supported image files in a directory."
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")
    return {
        f.relative_to(directory)
        for f in Path(directory).rglob("*")
        if f.is_file() and f.suffix.lower() in supported_extensions
    }
