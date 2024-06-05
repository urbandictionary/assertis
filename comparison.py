import os
import filecmp
import json
from md5_utils import md5_hash, md5_hash_image
from PIL import Image, ImageChops, ImageDraw
from models import FileReport, ReportData
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from io import BytesIO

exts = Image.registered_extensions()
supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}


def get_all_files(directory):
    return {
        f.relative_to(directory)
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in supported_extensions
    }


def compare_images(img1_path, img2_path, sensitivity):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    reasons = []

    if img1.mode != img2.mode:
        reasons.append(f"Mode changed from {img1.mode} to {img2.mode}")
    if img1.size != img2.size:
        reasons.append(f"Size changed from {img1.size} to {img2.size}")

    if img1.mode != img2.mode or img1.size != img2.size:
        return False, None, reasons

    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if bbox is None:
        return True, None, []
    else:
        diff_image = Image.new("RGBA", img1.size)
        draw = ImageDraw.Draw(diff_image)
        draw.rectangle(bbox, outline="red")

        # Calculate the extent of the change as a percentage of total pixels
        total_pixels = img1.size[0] * img1.size[1]
        changed_pixels = sum(diff.histogram())
        change_extent = (changed_pixels / total_pixels) * 100
        reasons.append(f"Pixels changed with extent {change_extent:.2f}%")

        return change_extent <= sensitivity, diff_image, reasons


def generate_html_report(report_dir, report_data):
    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template("report_template.html")

    html_content = template.render(report_data)

    with open(os.path.join(report_dir, "index.html"), "w") as report_file:
        report_file.write(html_content)


def run_comparison(expected, actual, output, sensitivity):
    expected_dir = Path(expected)
    actual_dir = Path(actual)
    output_dir = Path(output)
    template_path = Path(__file__).parent / "report_template.html"

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    report_data = ReportData()

    expected_images = get_all_files(expected_dir)
    actual_images = get_all_files(actual_dir)

    diff_images = {}

    for img_path in expected_images:
        if img_path not in actual_images:
            report_data.files.append(
                FileReport(
                    name=str(img_path),
                    output_expected_path=str(expected_dir / img_path),
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
                    output_expected_path=None,
                    output_actual_path=str(actual_dir / img_path),
                    diff_path=None,
                    comparison_result="added",
                    reason="Image added",
                )
            )
        else:
            output_expected_path = expected_dir / img_path
            output_actual_path = actual_dir / img_path

            if filecmp.cmp(output_expected_path, output_actual_path, shallow=False):
                report_data.files.append(
                    FileReport(
                        name=str(img_path),
                        output_expected_path=str(output_expected_path),
                        output_actual_path=str(output_actual_path),
                        diff_path=None,
                        comparison_result="unchanged",
                        reason="Image unchanged",
                    )
                )
            else:
                identical, diff_image, reasons = compare_images(
                    output_expected_path, output_actual_path, sensitivity
                )
                if identical:
                    report_data.files.append(
                        FileReport(
                            name=str(img_path),
                            output_expected_path=str(output_expected_path),
                            output_actual_path=str(output_actual_path),
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
                            output_expected_path=str(output_expected_path),
                            output_actual_path=str(output_actual_path),
                            diff_path=(
                                str(diff_path.relative_to(output_dir))
                                if diff_path
                                else None
                            ),
                            comparison_result="changed",
                            reason=", ".join(reasons),
                        )
                    )

    # Copy files to output directory based on MD5 hash
    for file_data in report_data.files:
        if file_data.output_expected_path:
            abs_output_expected_path = Path(file_data.output_expected_path)
            md5_hash_value = md5_hash(abs_output_expected_path)
            suffix = abs_output_expected_path.suffix
            img_output_path = output_dir / f"{md5_hash_value}{suffix}"
            shutil.copy(abs_output_expected_path, img_output_path)
            file_data.output_expected_path = str(
                img_output_path.relative_to(output_dir)
            )
            file_data.orginal_expected_path = str(abs_output_expected_path)

        if file_data.output_actual_path:
            abs_output_actual_path = Path(file_data.output_actual_path)
            md5_hash_value = md5_hash(abs_output_actual_path)
            suffix = abs_output_actual_path.suffix
            img_output_path = output_dir / f"{md5_hash_value}{suffix}"
            shutil.copy(abs_output_actual_path, img_output_path)
            file_data.output_actual_path = str(img_output_path.relative_to(output_dir))
            file_data.orginal_actual_path = str(abs_output_actual_path)

    # Write diff images to output directory
    for diff_path, diff_image in diff_images.items():
        diff_image.save(diff_path, format="PNG")

    # Update summary
    for file in report_data.files:
        report_data.summary[file.comparison_result] += 1

    report_data.summary = dict(report_data.summary)

    report_data.has_changes = any(
        file_data.comparison_result in ["changed", "added", "deleted"]
        for file_data in report_data.files
    )

    generate_html_report(output_dir, report_data)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(report_data.model_dump(), json_file, indent=4)

    return report_data.has_changes
