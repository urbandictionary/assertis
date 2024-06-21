import os
import shutil
import json
from pathlib import Path
from jinja2 import Environment, PackageLoader


def generate_html_report(report_dir, report):
    env = Environment(loader=PackageLoader("assertis", "templates"))
    template = env.get_template("report_template.html")

    html_content = template.render(report)

    with open(os.path.join(report_dir, "index.html"), "w") as report_file:
        report_file.write(html_content)


def write_report(report, output_dir):
    for file_data in report.files:
        if hasattr(file_data, "path_src_expected") and file_data.path_src_expected:
            path = Path(file_data.path_src_expected)
            file_data.path_out_expected = f"{file_data.md5_src_expected}{path.suffix}"
            shutil.copy(path, output_dir / file_data.path_out_expected)

        if hasattr(file_data, "path_src_actual") and file_data.path_src_actual:
            path = Path(file_data.path_src_actual)
            file_data.path_out_actual = f"{file_data.md5_src_actual}{path.suffix}"
            shutil.copy(path, output_dir / file_data.path_out_actual)

    for diff_path, diff_image in report.diff_images.items():
        diff_image.save(diff_path, format="PNG")

    # Initialize summary with all possible keys
    report.summary = {
        "added": 0,
        "changed": 0,
        "unchanged": 0,
        "deleted": 0,
    }

    for file in report.files:
        report.summary[file.type] += 1

    # Ensure all keys are present in the summary
    for key in ["added", "changed", "unchanged", "deleted"]:
        if key not in report.summary:
            report.summary[key] = 0

    report.has_changes = any(
        file_data.type in ["changed", "added", "deleted"] for file_data in report.files
    )

    generate_html_report(output_dir, report)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(
            report.model_dump(exclude={"diff_images"}),
            json_file,
            indent=4,
        )
