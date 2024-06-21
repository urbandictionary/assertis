import os
import random
import string
import requests
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
from pathlib import Path


# Function to generate a random string
def random_string(length=8):
    "Generate a random alphanumeric string."
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


# Function to download a random image
def download_image(output_path):
    "Download a random image from the internet."
    url = f"https://picsum.photos/200/300?random={random_string()}"
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)


# Function to create a directory structure
def create_directories(case_name):
    "Create the directory structure for a test case."
    os.makedirs(f"{case_name}/actual", exist_ok=True)
    os.makedirs(f"{case_name}/expected", exist_ok=True)
    Path(f"{case_name}/actual/.gitkeep").touch()
    Path(f"{case_name}/expected/.gitkeep").touch()


# Function to add text to an image
def add_text_to_image(image_path, text):
    "Overlay text onto an image."
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    width, height = img.size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    textwidth = text_bbox[2] - text_bbox[0]
    textheight = text_bbox[3] - text_bbox[1]
    x = (width - textwidth) / 2
    y = height - textheight - 10
    draw.text((x, y), text, font=font, fill="red")
    img.save(image_path)


# Function to resize an image
def resize_image(image_path, new_size):
    "Resize an image to the specified dimensions."
    img = Image.open(image_path)
    img_resized = img.resize(new_size)
    img_resized.save(image_path)


# Function to change mode of an image to RGBA
def change_mode_to_rgba(image_path):
    "Convert an image to RGBA mode."
    img = Image.open(image_path).convert("RGBA")
    img.save(image_path)


# Function to invert the colors of an image
def invert_image_colors(image_path):
    "Invert the colors of an image."
    img = Image.open(image_path)
    img_inverted = ImageOps.invert(img)
    img_inverted.save(image_path)


# Function to copy a file
def copy_file(src, dst):
    "Copy a file from the source to the destination."
    shutil.copy2(src, dst)


# Generate test cases
def generate_test_cases():
    "Generate various test cases for image comparison."
    # Case: Files added
    create_directories("files_added")
    download_image("files_added/actual/img1.jpg")

    # Case: Files removed
    create_directories("files_removed")
    download_image("files_removed/expected/img1.jpg")

    # Case: Files unchanged
    create_directories("files_unchanged")
    download_image("files_unchanged/expected/img1.jpg")
    copy_file(
        "files_unchanged/expected/img1.jpg",
        "files_unchanged/actual/img1.jpg",
    )

    # Case: Files changed
    create_directories("files_changed")
    download_image("files_changed/expected/img1.jpg")
    copy_file(
        "files_changed/expected/img1.jpg", "files_changed/actual/img1.jpg"
    )
    add_text_to_image("files_changed/actual/img1.jpg", "Changed")

    # Case: Lots of files
    create_directories("lots_of_files")
    for i in range(1, 11):
        expected_img_path = f"lots_of_files/expected/img_{i}.jpg"
        actual_img_path = f"lots_of_files/actual/img_{i}.jpg"
        download_image(expected_img_path)
        copy_file(expected_img_path, actual_img_path)
        if i % 2 == 0:
            add_text_to_image(actual_img_path, "Even")

    # Case: Files changed because of size
    create_directories("files_changed_size")
    download_image("files_changed_size/expected/img1.jpg")
    copy_file(
        "files_changed_size/expected/img1.jpg",
        "files_changed_size/actual/img1.jpg",
    )
    resize_image(
        "files_changed_size/actual/img1.jpg", (250, 375)
    )  # Resize to a different size

    # Case: Files changed because of mode
    create_directories("files_changed_mode")
    download_image("files_changed_mode/expected/img1.png")
    copy_file(
        "files_changed_mode/expected/img1.png",
        "files_changed_mode/actual/img1.png",
    )
    change_mode_to_rgba("files_changed_mode/actual/img1.png")

    # Case: Files changed a lot
    create_directories("files_changed_lot")
    download_image("files_changed_lot/expected/img1.jpg")
    copy_file(
        "files_changed_lot/expected/img1.jpg",
        "files_changed_lot/actual/img1.jpg",
    )
    invert_image_colors(
        "files_changed_lot/actual/img1.jpg"
    )  # Invert colors for significant change

    # Case: Empty directories
    create_directories("empty")


# Generate the test cases
generate_test_cases()

print("Test cases generated successfully.")
