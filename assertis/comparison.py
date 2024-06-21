import os
import filecmp
import json
from assertis.md5_utils import md5_hash, md5_hash_image
from assertis.file_utils import glob
from PIL import Image, ImageChops, ImageDraw
from assertis.models import (
    DisplayData,
    AddedFile,
    DeletedFile,
    ChangedFile,
    UnchangedFile,
)
import shutil
from pathlib import Path
from jinja2 import Environment, PackageLoader
from io import BytesIO


from PIL import Image, ImageChops


def compare_images(img1_path, img2_path, sensitivity):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    reasons = []

    if img1.format != img2.format:
        reasons.append(f"Format changed from {img1.format} to {img2.format}")
    if img1.mode != img2.mode:
        reasons.append(f"Mode changed from {img1.mode} to {img2.mode}")
    if img1.size != img2.size:
        reasons.append(f"Size changed from {img1.size} to {img2.size}")

    if reasons:
        return False, None, reasons

    # Calculate the difference between the images
    diff = ImageChops.difference(img1, img2)

    # Convert the difference image to grayscale
    diff_mask = diff.convert("L")

    # Create an RGBA image to highlight the differences
    diff_highlight = Image.new("RGBA", img1.size, (0, 0, 0, 0))
    threshold = 0  # You can adjust the threshold to control sensitivity

    # Highlight the changed pixels in red
    for x in range(diff.width):
        for y in range(diff.height):
            if diff_mask.getpixel((x, y)) > threshold:
                diff_highlight.putpixel((x, y), (255, 0, 0, 255))  # Highlight in red

    # Calculate the extent of the change as a percentage of total pixels
    total_pixels = img1.size[0] * img1.size[1]
    changed_pixels = sum(1 for pixel in diff_mask.getdata() if pixel > threshold)
    change_extent = (changed_pixels / total_pixels) * 100
    reasons.append(f"Pixels changed with extent {change_extent:.2f}%")

    return change_extent <= sensitivity, diff_highlight, reasons


def generate_html_report(report_dir, display_data):
    env = Environment(loader=PackageLoader("assertis", "templates"))
    template = env.get_template("report_template.html")

    html_content = template.render(display_data)

    with open(os.path.join(report_dir, "index.html"), "w") as report_file:
        report_file.write(html_content)


def write_report(display_data, diff_images, output_dir):
    for file_data in display_data.files:
        if hasattr(file_data, "path_src_expected") and file_data.path_src_expected:
            path = Path(file_data.path_src_expected)
            file_data.path_out_expected = f"{md5_hash(path)}{path.suffix}"
            shutil.copy(path, output_dir / file_data.path_out_expected)

        if hasattr(file_data, "path_src_actual") and file_data.path_src_actual:
            path = Path(file_data.path_src_actual)
            file_data.path_out_actual = f"{md5_hash(path)}{path.suffix}"
            shutil.copy(path, output_dir / file_data.path_out_actual)

    for diff_path, diff_image in diff_images.items():
        diff_image.save(diff_path, format="PNG")

    # Initialize summary with all possible keys
    display_data.summary = {"added": 0, "changed": 0, "unchanged": 0, "deleted": 0}

    for file in display_data.files:
        display_data.summary[file.comparison_result] += 1

    # Ensure all keys are present in the summary
    for key in ["added", "changed", "unchanged", "deleted"]:
        if key not in display_data.summary:
            display_data.summary[key] = 0

    display_data.has_changes = any(
        file_data.comparison_result in ["changed", "added", "deleted"]
        for file_data in display_data.files
    )

    generate_html_report(output_dir, display_data)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(display_data.model_dump(), json_file, indent=4)

    return display_data.has_changes


def run_comparison(expected, actual, output, sensitivity):
    expected_dir = Path(expected)
    actual_dir = Path(actual)
    output_dir = Path(output)

    display_data = DisplayData()

    expected_images = glob(expected_dir)
    actual_images = glob(actual_dir)

    diff_images = {}

    for img_path in expected_images:
        if img_path not in actual_images:
            display_data.files.append(
                DeletedFile(
                    name=str(img_path),
                    path_src_expected=str(expected_dir / img_path),
                    path_out_expected=None,
                    reasons=["Image deleted"],
                )
            )

    for img_path in actual_images:
        if img_path not in expected_images:
            display_data.files.append(
                AddedFile(
                    name=str(img_path),
                    path_src_actual=str(actual_dir / img_path),
                    path_out_actual=None,
                    reasons=["Image added"],
                )
            )
        else:
            path_src_expected = expected_dir / img_path
            path_src_actual = actual_dir / img_path

            if filecmp.cmp(path_src_expected, path_src_actual, shallow=False):
                display_data.files.append(
                    UnchangedFile(
                        name=str(img_path),
                        path_src_expected=str(path_src_expected),
                        path_src_actual=str(path_src_actual),
                        path_out_expected=None,
                        path_out_actual=None,
                        reasons=["Image unchanged"],
                    )
                )
            else:
                identical, diff_image, reasons = compare_images(
                    path_src_expected, path_src_actual, sensitivity
                )
                if identical:
                    display_data.files.append(
                        UnchangedFile(
                            name=str(img_path),
                            path_src_expected=str(path_src_expected),
                            path_src_actual=str(path_src_actual),
                            path_out_expected=None,
                            path_out_actual=None,
                            reasons=["Image unchanged"],
                        )
                    )
                else:
                    diff_path = None
                    if diff_image:
                        md5_hash_value = md5_hash_image(diff_image)
                        diff_path = output_dir / f"{md5_hash_value}.png"
                        diff_images[str(diff_path)] = diff_image
                    display_data.files.append(
                        ChangedFile(
                            name=str(img_path),
                            path_src_expected=str(path_src_expected),
                            path_src_actual=str(path_src_actual),
                            path_out_expected=None,
                            path_out_actual=None,
                            diff_path=(
                                str(diff_path.relative_to(output_dir))
                                if diff_path
                                else None
                            ),
                            reasons=reasons,
                        )
                    )

    return write_report(display_data, diff_images, output_dir)
