import click
import json
from pathlib import Path
import sys
import shutil
from assertis.models import (
    ReportData,
    AddedFile,
    DeletedFile,
    ChangedFile,
    UnchangedFile,
)


def verify_report(report, expected):
    errors = []
    for file in report.files:
        if file.output_expected_path and not Path(file.original_expected_path).exists():
            errors.append(
                f"Expected file {file.original_expected_path} does not exist."
            )
        if file.output_actual_path and not Path(file.original_actual_path).exists():
            errors.append(f"Actual file {file.original_actual_path} does not exist.")
        if isinstance(file, DeletedFile) and Path(file.original_expected_path).exists():
            errors.append(
                f"Expected file {file.original_expected_path} should be deleted but exists."
            )
        if isinstance(file, AddedFile) and not Path(file.original_actual_path).exists():
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


def apply_changes(report, expected, dry_run):
    for file in report.files:
        if isinstance(file, AddedFile):
            target_path = Path(expected) / file.name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if not dry_run:
                shutil.copy(file.original_actual_path, target_path)
            print(
                f"Would add file {target_path}"
                if dry_run
                else f"Added file {target_path}"
            )
        elif isinstance(file, DeletedFile):
            target_path = Path(expected) / file.name
            if not dry_run:
                target_path.unlink()
            print(
                f"Would delete file {target_path}"
                if dry_run
                else f"Deleted file {target_path}"
            )
        elif isinstance(file, ChangedFile):
            target_path = Path(expected) / file.name
            if not dry_run:
                shutil.copy(file.original_actual_path, target_path)
            print(
                f"Would change file {target_path}"
                if dry_run
                else f"Changed file {target_path}"
            )


@click.command(
    help="Apply changes to the expected directory based on the comparison report."
)
@click.argument("output")
@click.argument("expected")
@click.option("--dry-run", is_flag=True, help="Run the command in dry run mode.")
def fix(output, expected, dry_run):
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

    apply_changes(report, expected, dry_run)
