import click
import json
from pathlib import Path
import sys
import shutil
from assertis.cmd_verify import verify_report
from assertis.models import (
    Report,
    AddedFile,
    DeletedFile,
    ChangedFile,
    UnchangedFile,
)


def apply_changes(report, output_dir, expected_dir, dry_run):
    for file in report.files:
        target_path = Path(expected_dir) / file.name
        source_path = Path(output_dir) / file.actual_out_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(file, AddedFile) or isinstance(file, ChangedFile):
            if not dry_run:
                shutil.copy(source_path, target_path)
            print(f"{'Would add' if dry_run else 'Added'} file {target_path}")

        elif isinstance(file, DeletedFile):
            if not dry_run:
                if target_path.exists():
                    target_path.unlink()
            print(f"{'Would delete' if dry_run else 'Deleted'} file {target_path}")


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
        report = json.load(f)

    report = Report(**report)

    errors = verify_report(report, output_dir, Path(expected))
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    apply_changes(report, output_dir, Path(expected), dry_run)
