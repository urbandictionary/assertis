import sys
from pathlib import Path

import click

from assertis.comparison import write_comparison
from assertis.models import report_to_string


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.argument("output")
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def compare(expected, actual, output, sensitivity):
    "Compare images in the expected and actual directories."
    report_dir = Path(output)
    if report_dir.exists():
        if any(report_dir.iterdir()):
            click.echo(
                "Output directory already exists and is not empty. Please remove it first."
            )
            sys.exit(1)
    else:
        report_dir.mkdir(parents=True)

    report = write_comparison(expected, actual, report_dir, sensitivity)
    click.echo(report_to_string(report, output, expected))
    if report.has_changes:
        sys.exit(1)
    else:
        sys.exit(0)
