import sys
import click
from comparison import run_comparison
from pathlib import Path


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--output",
    prompt="Output directory",
    help="Directory to store the output report and images.",
)
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def compare(expected, actual, output, sensitivity):
    output_dir = Path(output)
    if output_dir.exists() and any(output_dir.iterdir()):
        print(
            "Output directory already exists and is not empty. Please remove it first."
        )
        sys.exit(1)

    has_changes = run_comparison(expected, actual, output_dir, sensitivity)
    if has_changes:
        sys.exit(1)
    else:
        sys.exit(0)