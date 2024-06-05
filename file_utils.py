from pathlib import Path
from PIL import Image

exts = Image.registered_extensions()
supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}

def glob(directory):
    return {
        f.relative_to(directory)
        for f in Path(directory).rglob("*")
        if f.is_file() and f.suffix.lower() in supported_extensions
    }
