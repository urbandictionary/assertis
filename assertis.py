import os
import sys
import filecmp
import json
import hashlib
from PIL import Image, ImageChops, ImageDraw
import click
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from io import BytesIO  # Import BytesIO for in-memory binary streams

# Determine supported image extensions
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


def md5_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def md5_hash_image(image):
    hasher = hashlib.md5()
    with BytesIO() as output:
        image.save(output, format="PNG")
        hasher.update(output.getvalue())
    return hasher.hexdigest()


def run_comparison(expected, actual, output, sensitivity):
    expected_dir = Path(expected)
    actual_dir = Path(actual)
    output_dir = Path(output)
    template_path = Path(__file__).parent / "report_template.html"

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    report_data = {"files": [], "has_changes": False, "summary": defaultdict(int)}

    expected_images = get_all_files(expected_dir)
    actual_images = get_all_files(actual_dir)

    diff_images = {}

    for img_path in expected_images:
        if img_path not in actual_images:
            report_data["files"].append(
                {
                    "name": str(img_path),
                    "expected_path": str(expected_dir / img_path),
                    "actual_path": None,
                    "diff": None,
                    "comparison_result": "deleted",
                    "reason": "Image deleted",
                }
            )

    for img_path in actual_images:
        if img_path not in expected_images:
            report_data["files"].append(
                {
                    "name": str(img_path),
                    "expected_path": None,
                    "actual_path": str(actual_dir / img_path),
                    "diff": None,
                    "comparison_result": "added",
                    "reason": "Image added",
                }
            )
        else:
            expected_img_path = expected_dir / img_path
            actual_img_path = actual_dir / img_path

            if filecmp.cmp(expected_img_path, actual_img_path, shallow=False):
                report_data["files"].append(
                    {
                        "name": str(img_path),
                        "expected_path": str(expected_img_path),
                        "actual_path": str(actual_img_path),
                        "diff": None,
                        "comparison_result": "unchanged",
                        "reason": "Image unchanged",
                    }
                )
            else:
                identical, diff_image, reasons = compare_images(
                    expected_img_path, actual_img_path, sensitivity
                )
                if identical:
                    report_data["files"].append(
                        {
                            "name": str(img_path),
                            "expected_path": str(expected_img_path),
                            "actual_path": str(actual_img_path),
                            "diff": None,
                            "comparison_result": "unchanged",
                            "reason": "Image unchanged",
                        }
                    )
                else:
                    diff_path = None
                    if diff_image:
                        md5_hash_value = md5_hash_image(diff_image)
                        diff_path = output_dir / f"{md5_hash_value}.png"
                        diff_images[str(diff_path)] = diff_image
                    report_data["files"].append(
                        {
                            "name": str(img_path),
                            "expected_path": str(expected_img_path),
                            "actual_path": str(actual_img_path),
                            "diff": (
                                str(diff_path.relative_to(output_dir))
                                if diff_path
                                else None
                            ),
                            "comparison_result": "changed",
                            "reason": ", ".join(reasons),
                        }
                    )

    # Copy files to output directory based on MD5 hash
    for file_data in report_data["files"]:
        if file_data["expected_path"]:
            abs_expected_path = Path(file_data["expected_path"])
            md5_hash_value = md5_hash(abs_expected_path)
            suffix = abs_expected_path.suffix
            img_output_path = output_dir / f"{md5_hash_value}{suffix}"
            shutil.copy(abs_expected_path, img_output_path)
            file_data["expected_path"] = str(img_output_path.relative_to(output_dir))
            file_data["expected_abs_path"] = str(abs_expected_path)

        if file_data["actual_path"]:
            abs_actual_path = Path(file_data["actual_path"])
            md5_hash_value = md5_hash(abs_actual_path)
            suffix = abs_actual_path.suffix
            img_output_path = output_dir / f"{md5_hash_value}{suffix}"
            shutil.copy(abs_actual_path, img_output_path)
            file_data["actual_path"] = str(img_output_path.relative_to(output_dir))
            file_data["actual_abs_path"] = str(abs_actual_path)

    # Write diff images to output directory
    for diff_path, diff_image in diff_images.items():
        diff_image.save(diff_path, format="PNG")

    # Update summary
    for file in report_data["files"]:
        report_data["summary"][file["comparison_result"]] += 1

    report_data["summary"] = dict(report_data["summary"])

    report_data["has_changes"] = any(
        file_data["comparison_result"] in ["changed", "added", "deleted"]
        for file_data in report_data["files"]
    )

    generate_html_report(output_dir, report_data)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(report_data, json_file, indent=4)

    return report_data["has_changes"]


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--output",
    prompt="Output directory",
    help="Directory to store the output report and images.",
)
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def compare(expected, actual, output, sensitivity):
    output_dir = Path(output)
    if output_dir.exists() and any(output_dir.iterdir()):
        print(
            "Output directory already exists and is not empty. Please remove it first."
        )
        sys.exit(1)

    has_changes = run_comparison(expected, actual, output_dir, sensitivity)
    if has_changes:
        sys.exit(1)
    else:
        sys.exit(0)


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def serve(expected, actual, sensitivity):
    import http.server
    import socketserver
    import threading
    import time
    import tempfile
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, expected, actual, output, sensitivity):
            self.expected = expected
            self.actual = actual
            self.output = output
            self.sensitivity = sensitivity

        def on_any_event(self, event):
            run_comparison(self.expected, self.actual, self.output, self.sensitivity)

    with tempfile.TemporaryDirectory() as temp_output:
        output_dir = Path(temp_output)

        # Run initial comparison
        run_comparison(expected, actual, output_dir, sensitivity)

        handler = ChangeHandler(expected, actual, output_dir, sensitivity)
        observer = Observer()
        observer.schedule(handler, path=expected, recursive=True)
        observer.schedule(handler, path=actual, recursive=True)
        observer.start()

        os.chdir(output_dir)
        PORT = 8001
        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", PORT), Handler)

        print(f"Serving at port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        observer.stop()
        observer.join()


@click.group()
def assertis():
    pass


assertis.add_command(compare)
assertis.add_command(serve)

if __name__ == "__main__":
    assertis()
