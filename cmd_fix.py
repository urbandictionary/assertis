import click
import json
from pathlib import Path
import sys
import shutil
from models import ReportData


def verify_report(report, expected):
    errors = []
    for file in report.files:
        if file.output_expected_path and not Path(file.original_expected_path).exists():
            errors.append(f"Expected file {file.original_expected_path} does not exist.")
        if file.output_actual_path and not Path(file.original_actual_path).exists():
            errors.append(f"Actual file {file.original_actual_path} does not exist.")
        if (
            file.comparison_result == "deleted"
            and Path(file.original_expected_path).exists()
        ):
            errors.append(
                f"Expected file {file.original_expected_path} should be deleted but exists."
            )
        if (
            file.comparison_result == "added"
            and not Path(file.original_actual_path).exists()
        ):
            errors.append(
                f"Actual file {file.original_actual_path} should be added but does not exist."
            )
        # Check if files at output_expected_path and output_actual_path relative to output directory exist
        if (
            file.output_expected_path
            and not Path(expected) / file.output_expected_path.exists()
        ):
            errors.append(
                f"Expected file {Path(expected) / file.output_expected_path} does not exist."
            )
        if (
            file.output_actual_path
            and not Path(expected) / file.output_actual_path.exists()
        ):
            errors.append(
                f"Actual file {Path(expected) / file.output_actual_path} does not exist."
            )
    return errors


def apply_changes(report, expected):
    for file in report.files:
        if file.comparison_result == "added":
            if file.original_actual_path:
                target_path = Path(expected) / file.name
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file.original_actual_path, target_path)
                print(f"Added file {target_path}")
        elif file.comparison_result == "deleted":
            target_path = Path(expected) / file.name
            if target_path.exists():
                target_path.unlink()
                print(f"Deleted file {target_path}")
        elif file.comparison_result == "changed":
            if file.original_actual_path:
                target_path = Path(expected) / file.name
                shutil.copy(file.original_actual_path, target_path)
                print(f"Changed file {target_path}")


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

    errors = verify_report(report, expected)
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    apply_changes(report, expected)
