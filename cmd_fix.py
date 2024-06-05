import click
import json
from pathlib import Path
from models import ReportData


@click.command()
@click.argument("output")
@click.argument("actual")
def fix(output, actual):
    output_dir = Path(output)
    report_file = output_dir / "report.json"

    if not report_file.exists():
        print(f"Report file {report_file} does not exist.")
        return

    with open(report_file, "r") as f:
        report_data = json.load(f)

    try:
        report = ReportData(**report_data)
        print("Report data is valid.")
    except Exception as e:
        print(f"Report data is invalid: {e}")


if __name__ == "__main__":
    fix()
