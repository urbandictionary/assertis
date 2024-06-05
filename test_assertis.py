import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner
from assertis import assertis  # Replace with the actual name of your script module


def generate_report(cases_dir):
    cases_path = Path(cases_dir)
    expected_dir = cases_path / "expected"
    actual_dir = cases_path / "actual"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "output"

        runner = CliRunner()
        result = runner.invoke(
            assertis,
            [
                str(expected_dir),
                str(actual_dir),
                "--output",
                str(output_dir),
                "--sensitivity",
                "0",
            ],
            catch_exceptions=False,  # Ensure that exceptions are not caught and displayed in stderr
        )

        report_path = output_dir / "report.json"
        if not report_path.exists():
            raise FileNotFoundError(f"report.json not found in {output_dir}")

        with open(report_path, "r") as report_file:
            report_data = json.load(report_file)

    return result.exit_code, report_data


def test_assertis_files_unchanged():
    exit_code, report_data = generate_report(Path("cases/files_unchanged"))
    assert exit_code == 1
    assert report_data["has_changes"] is True
    assert report_data["summary"] == {"added": 1, "deleted": 1}
