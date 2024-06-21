import os
import filecmp
import json
from assertis.md5_utils import md5_hash, md5_hash_image
from assertis.file_utils import glob
from PIL import Image, ImageChops, ImageDraw
from assertis.models import (
    Report,
    AddedFile,
    DeletedFile,
    ChangedFile,
    UnchangedFile,
)
from assertis.write import generate_html_report, write_report
from pathlib import Path
from io import BytesIO


def compare_images(img1_path, img2_path, sensitivity):
    "Compare two images and highlight differences."
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


def md5_path(path):
    return f"{md5_hash(path)}{path.suffix}"


def run_comparison(expected, actual, output, sensitivity):
    "Run the comparison between expected and actual directories."
    expected_dir = Path(expected)
    actual_dir = Path(actual)
    output_dir = Path(output)

    report = Report()

    expected_paths = glob(expected_dir)
    actual_paths = glob(actual_dir)

    for path in expected_paths:
        if path not in actual_paths:
            report.files.append(
                DeletedFile(
                    expected_md5=md5_hash(expected_dir / path),
                    name=str(path),
                    reasons=["Image deleted"],
                )
            )

    for path in actual_paths:
        expected_path = expected_dir / path
        actual_path = actual_dir / path

        if path not in expected_paths:
            report.files.append(
                AddedFile(
                    actual_file=md5_path(actual_path),
                    actual_md5=md5_hash(actual_path),
                    name=str(path),
                    reasons=["Image added"],
                )
            )
            report.outputs[str(md5_path(actual_path))] = actual_path
        else:
            if filecmp.cmp(expected_path, actual_path, shallow=False):
                report.files.append(
                    UnchangedFile(
                        actual_file=md5_path(actual_path),
                        actual_md5=md5_hash(actual_path),
                        expected_file=md5_path(actual_path),
                        expected_md5=md5_hash(expected_path),
                        name=str(path),
                        reasons=["Image unchanged"],
                    )
                )
                report.outputs[md5_path(actual_path)] = actual_path
            else:
                identical, diff_image, reasons = compare_images(
                    expected_path, actual_path, sensitivity
                )
                if identical:
                    report.files.append(
                        UnchangedFile(
                            actual_file=md5_path(actual_path),
                            expected_file=md5_path(actual_path),
                            md5_actual=md5_hash(actual_path),
                            md5_expected=md5_hash(expected_path),
                            name=str(path),
                            reasons=["Image unchanged"],
                        )
                    )
                    report.outputs[md5_path(actual_path)] = actual_path
                else:
                    diff_file = None
                    if diff_image:
                        md5_hash_value = md5_hash_image(diff_image)
                        diff_file = f"{md5_hash_value}.png"
                        report.outputs[diff_file] = diff_image
                    report.files.append(
                        ChangedFile(
                            actual_file=md5_path(actual_path),
                            actual_md5=md5_hash(actual_path),
                            diff_file=diff_file,
                            expected_file=md5_path(expected_path),
                            expected_md5=md5_hash(expected_path),
                            name=str(path),
                            reasons=reasons,
                        )
                    )
                    report.outputs[md5_path(actual_path)] = actual_path
                    report.outputs[md5_path(expected_path)] = expected_path

    write_report(report, output_dir)
    return report
