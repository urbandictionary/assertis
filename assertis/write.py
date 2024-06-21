import json
import os
import shutil
from pathlib import Path

from jinja2 import Environment, PackageLoader


def generate_html_report(report_dir, report):
    "Generate an HTML report from the comparison results."
    env = Environment(loader=PackageLoader("assertis", "templates"))
    template = env.get_template("report_template.html")

    html_content = template.render(report)

    with open(os.path.join(report_dir, "index.html"), "w") as report_file:
        report_file.write(html_content)


def write_report(report, output_dir):
    "Write the comparison report to the output directory."
    for path, output in report.outputs.items():
        if isinstance(output, Path):
            shutil.copy(output, output_dir / path)
        else:
            output.save(output_dir / path, format="PNG")

    # Initialize summary with all possible keys
    report.summary = {
        "added": 0,
        "changed": 0,
        "unchanged": 0,
        "deleted": 0,
    }

    for file in report.files:
        report.summary[file.type] += 1

    report.has_changes = bool(
        report.summary["added"]
        or report.summary["changed"]
        or report.summary["deleted"]
    )

    generate_html_report(output_dir, report)

    with open(output_dir / "report.json", "w") as json_file:
        json.dump(
            report.model_dump(exclude={"outputs"}),
            json_file,
            indent=4,
        )
