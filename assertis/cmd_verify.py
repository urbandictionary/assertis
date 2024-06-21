import click
from pathlib import Path
import json
import sys
from assertis.models import Report, AddedFile, DeletedFile, ChangedFile, UnchangedFile


@click.command(help="Verify the comparison report.")
@click.argument("output")
@click.argument("expected")
def verify(output, expected):
    output_dir = Path(output)
    expected_dir = Path(expected)
    report_file = output_dir / "report.json"

    if not report_file.exists():
        print(f"Report file {report_file} does not exist.", file=sys.stderr)
        return

    with open(report_file, "r") as f:
        report_data = json.load(f)

    report = Report(**report_data)
    errors = verify_report(report, expected_dir)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    else:
        print("Verification successful. No errors found.")


from assertis.md5_utils import md5_hash

def should_exist(file_path, file_type, errors, expected_md5):
    if not Path(file_path).exists():
        errors.append(f"{file_type} file {file_path} should exist but does not exist.")
    elif md5_hash(file_path) != expected_md5:
        errors.append(f"{file_type} file {file_path} exists but its MD5 does not match.")


def should_not_exist(file_path, file_type, errors):
    if Path(file_path).exists():
        errors.append(f"{file_type} file {file_path} should not exist but does exist.")


def verify_report(report, expected_dir):
    errors = []
    expected_path = Path(expected_dir)

    for file in report.files:
        if isinstance(file, DeletedFile):
            should_not_exist(file.expected_src_path, "Expected", errors)
        elif isinstance(file, AddedFile):
            should_exist(file.actual_src_path, "Actual", errors, file.actual_md5)
        elif isinstance(file, ChangedFile):
            should_exist(file.actual_src_path, "Actual", errors, file.actual_md5)
            should_exist(file.expected_src_path, "Expected", errors, file.expected_md5)
        elif isinstance(file, UnchangedFile):
            should_exist(file.actual_src_path, "Actual", errors, file.actual_md5)
            should_exist(file.expected_src_path, "Expected", errors, file.expected_md5)

    return errors
