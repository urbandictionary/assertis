import click
import json
from pathlib import Path
from models import ReportData


@click.command()
@click.argument("output")
@click.argument("expected")
def fix(output, expected):
    output_dir = Path(output)
    report_file = output_dir / "report.json"

    if not report_file.exists():
        print(f"Report file {report_file} does not exist.")
        return

    with open(report_file, "r") as f:
        report_data = json.load(f)

    report = ReportData(**report_data)

    errors = []
    for file in report.files:
        if file.expected_path and not Path(file.expected_abs_path).exists():
            errors.append(f"Expected file {file.expected_abs_path} does not exist.")
        if file.actual_path and not Path(file.actual_abs_path).exists():
            errors.append(f"Actual file {file.actual_abs_path} does not exist.")
        if (
            file.comparison_result == "deleted"
            and Path(file.expected_abs_path).exists()
        ):
            errors.append(
                f"Expected file {file.expected_abs_path} should be deleted but exists."
            )
        if (
            file.comparison_result == "added"
            and not Path(file.actual_abs_path).exists()
        ):
            errors.append(
                f"Actual file {file.actual_abs_path} should be added but does not exist."
            )
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)


if __name__ == "__main__":
    fix()
