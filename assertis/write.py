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
        if hasattr(file_data, "expected_src_path") and file_data.expected_src_path:
            path = Path(file_data.expected_src_path)
            file_data.expected_out_path = f"{file_data.expected_src_md5}{path.suffix}"
            shutil.copy(path, output_dir / file_data.expected_out_path)

        if hasattr(file_data, "actual_src_path") and file_data.actual_src_path:
            path = Path(file_data.actual_src_path)
            file_data.actual_out_path = f"{file_data.actual_src_md5}{path.suffix}"
            shutil.copy(path, output_dir / file_data.actual_out_path)

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
