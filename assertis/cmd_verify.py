import click
from pathlib import Path
import json
import sys
from assertis.models import Report, AddedFile, DeletedFile, ChangedFile


@click.command(help="Verify the comparison report.")
@click.argument("output")
@click.argument("expected")
def verify(output, expected):
    output_dir = Path(output)
    report_file = output_dir / "report.json"

    if not report_file.exists():
        print(f"Report file {report_file} does not exist.", file=sys.stderr)
        return

    with open(report_file, "r") as f:
        report_data = json.load(f)

    report = Report(**report_data)
    errors = verify_report(report, expected)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    else:
        print("Verification successful. No errors found.")


def verify_report(report, expected):
    def check_file_exists(file_path, should_exist, error_message):
        if should_exist and not Path(file_path).exists():
            errors.append(error_message)
        elif not should_exist and Path(file_path).exists():
            errors.append(error_message)
    errors = []
    expected_path = Path(expected)

    for file in report.files:
        if isinstance(file, DeletedFile):
            check_file_exists(file.path_src_expected, False, f"Expected file {file.path_src_expected} should be deleted but exists.")
        elif isinstance(file, AddedFile):
            check_file_exists(file.path_src_actual, True, f"Actual file {file.path_src_actual} should be added but does not exist.")
        elif isinstance(file, ChangedFile):
            check_file_exists(file.path_src_actual, True, f"Actual file {file.path_src_actual} does not exist.")
            check_file_exists(file.path_src_expected, True, f"Expected file {file.path_src_expected} does not exist.")
        elif isinstance(file, UnchangedFile):
            check_file_exists(file.path_src_actual, True, f"Actual file {file.path_src_actual} does not exist.")
            check_file_exists(file.path_src_expected, True, f"Expected file {file.path_src_expected} does not exist.")

    return errors
