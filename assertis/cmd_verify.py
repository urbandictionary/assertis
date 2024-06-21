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
        print(f"Report file {report_file} does not exist.")
        return

    with open(report_file, "r") as f:
        report = json.load(f)

    report = Report(**report)

    errors = verify_report(report, expected)
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("Verification successful. No errors found.")

def verify_report(report, expected):
    errors = []
    for file in report.files:
        if file.path_out_expected and not Path(file.path_src_expected).exists():
            errors.append(f"Expected file {file.path_src_expected} does not exist.")
        if file.path_out_actual and not Path(file.path_src_actual).exists():
            errors.append(f"Actual file {file.path_src_actual} does not exist.")
        if isinstance(file, DeletedFile) and Path(file.path_src_expected).exists():
            errors.append(
                f"Expected file {file.path_src_expected} should be deleted but exists."
            )
        if isinstance(file, AddedFile) and not Path(file.path_src_actual).exists():
            errors.append(
                f"Actual file {file.path_src_actual} should be added but does not exist."
            )
        # Check if files at path_out_expected and path_out_actual relative to output directory exist
        if (
            file.path_out_expected
            and not Path(expected) / file.path_out_expected.exists()
        ):
            errors.append(
                f"Expected file {Path(expected) / file.path_out_expected} does not exist."
            )
        if file.path_out_actual and not Path(expected) / file.path_out_actual.exists():
            errors.append(
                f"Actual file {Path(expected) / file.path_out_actual} does not exist."
            )
    return errors
