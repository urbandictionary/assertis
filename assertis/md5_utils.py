import hashlib
from io import BytesIO

from PIL import Image


def md5_hash(file_path):
    "Compute the MD5 hash of a file."
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def md5_hash_image(image):
    "Compute the MD5 hash of an image."
    hasher = hashlib.md5()
    with BytesIO() as output:
        image.save(output, format="PNG")
        hasher.update(output.getvalue())
    return hasher.hexdigest()
