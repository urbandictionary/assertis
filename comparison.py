import os
import filecmp
import json
from md5_utils import md5_hash, md5_hash_image
from file_utils import glob
from PIL import Image, ImageChops, ImageDraw
from models import FileReport, ReportData
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
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

    if img1.mode != img2.mode or img1.size != img2.size:
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


def generate_html_report(report_dir, report_data):
    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template("report_template.html")

    html_content = template.render(report_data)

    with open(os.path.join(report_dir, "index.html"), "w") as report_file:
        report_file.write(html_content)


def finish(report_data, diff_images, output_dir):
    for file_data in report_data.files:
        if file_data.original_expected_path:
            path = Path(file_data.original_expected_path)
            file_data.output_expected_path = f"{md5_hash(path)}{path.suffix}"
            shutil.copy(path, output_dir / file_data.output_expected_path)

        if file_data.original_actual_path:
            path = Path(file_data.original_actual_path)
            file_data.output_actual_path = f"{md5_hash(path)}{path.suffix}"
            shutil.copy(path, output_dir / file_data.output_actual_path)

    for diff_path, diff_image in diff_images.items():
        diff_image.save(diff_path, format="PNG")

    # Initialize summary with all possible keys
    report_data.summary = {"added": 0, "changed": 0, "unchanged": 0, "deleted": 0}

    for file in report_data.files:
        report_data.summary[file.comparison_result] += 1

    # Ensure all keys are present in the summary
    for key in ["added", "changed", "unchanged", "deleted"]:
        if key not in report_data.summary:
            report_data.summary[key] = 0

    report_data.has_changes = any(
        file_data.comparison_result in ["changed", "added", "deleted"]
        for file_data in report_data.files
    )

    generate_html_report(output_dir, report_data)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(report_data.model_dump(), json_file, indent=4)

    return report_data.has_changes


def run_comparison(expected, actual, output, sensitivity):
    expected_dir = Path(expected)
    actual_dir = Path(actual)
    output_dir = Path(output)

    report_data = ReportData()

    expected_images = glob(expected_dir)
    actual_images = glob(actual_dir)

    diff_images = {}

    for img_path in expected_images:
        if img_path not in actual_images:
            report_data.files.append(
                FileReport(
                    name=str(img_path),
                    original_expected_path=str(expected_dir / img_path),
                    original_actual_path=None,
                    output_expected_path=None,
                    output_actual_path=None,
                    diff_path=None,
                    comparison_result="deleted",
                    reason="Image deleted",
                )
            )

    for img_path in actual_images:
        if img_path not in expected_images:
            report_data.files.append(
                FileReport(
                    name=str(img_path),
                    original_expected_path=None,
                    original_actual_path=str(actual_dir / img_path),
                    output_expected_path=None,
                    output_actual_path=None,
                    diff_path=None,
                    comparison_result="added",
                    reason="Image added",
                )
            )
        else:
            original_expected_path = expected_dir / img_path
            original_actual_path = actual_dir / img_path

            if filecmp.cmp(original_expected_path, original_actual_path, shallow=False):
                report_data.files.append(
                    FileReport(
                        name=str(img_path),
                        original_expected_path=str(original_expected_path),
                        original_actual_path=str(original_actual_path),
                        output_expected_path=None,
                        output_actual_path=None,
                        diff_path=None,
                        comparison_result="unchanged",
                        reason="Image unchanged",
                    )
                )
            else:
                identical, diff_image, reasons = compare_images(
                    original_expected_path, original_actual_path, sensitivity
                )
                if identical:
                    report_data.files.append(
                        FileReport(
                            name=str(img_path),
                            original_expected_path=str(original_expected_path),
                            original_actual_path=str(original_actual_path),
                            output_expected_path=None,
                            output_actual_path=None,
                            diff_path=None,
                            comparison_result="unchanged",
                            reason="Image unchanged",
                        )
                    )
                else:
                    diff_path = None
                    if diff_image:
                        md5_hash_value = md5_hash_image(diff_image)
                        diff_path = output_dir / f"{md5_hash_value}.png"
                        diff_images[str(diff_path)] = diff_image
                    report_data.files.append(
                        FileReport(
                            name=str(img_path),
                            original_expected_path=str(original_expected_path),
                            original_actual_path=str(original_actual_path),
                            output_expected_path=None,
                            output_actual_path=None,
                            diff_path=(
                                str(diff_path.relative_to(output_dir))
                                if diff_path
                                else None
                            ),
                            comparison_result="changed",
                            reason=", ".join(reasons),
                        )
                    )

    return finish(report_data, diff_images, output_dir)
