import json
import shutil
import sys
from pathlib import Path

import click

from assertis.cmd_verify import verify_report
from assertis.models import (AddedFile, ChangedFile, DeletedFile, Report,
                             UnchangedFile)


def apply_changes(report, report_dir, expected_dir, dry_run):
    "Apply changes to the expected directory based on the report."
    for file in report.files:
        target_path = Path(expected_dir) / file.name
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(file, AddedFile) or isinstance(file, ChangedFile):
            if not dry_run:
                shutil.copy(Path(report_dir) / file.actual_file, target_path)
            print(f"{'Would add' if dry_run else 'Added'} file {target_path}")

        elif isinstance(file, DeletedFile):
            if not dry_run:
                target_path.unlink()
            print(f"{'Would delete' if dry_run else 'Deleted'} file {target_path}")


@click.command()
@click.argument("expected")
@click.argument("report")
@click.option("--dry-run", is_flag=True, help="Run the command in dry run mode.")
def fix(expected, report, dry_run):
    "Apply changes to the expected directory."
    report_dir = Path(report)
    report_file = report_dir / "report.json"

    if not report_file.exists():
        print(f"Report file {report_file} does not exist.")
        return

    with open(report_file, "r") as f:
        report = json.load(f)

    report = Report(**report)

    errors = verify_report(report, report_dir, Path(expected))
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    apply_changes(report, report_dir, Path(expected), dry_run)
