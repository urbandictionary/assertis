import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner
from assertis import assertis  # Replace with the actual name of your script module
from models import ReportData


def generate_report(cases_dir):
    cases_path = Path(cases_dir)
    expected_dir = cases_path / "expected"
    actual_dir = cases_path / "actual"

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)

        runner = CliRunner()
        result = runner.invoke(
            assertis,
            [
                "compare",
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
            report_data = ReportData(**json.load(report_file))

    return result.exit_code, report_data


def test_empty():
    exit_code, report_data = generate_report(Path("cases/empty"))
    assert exit_code == 0
    assert report_data.has_changes is False
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {}


def test_added():
    exit_code, report_data = generate_report(Path("cases/files_added"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"added": 1}


def test_changed():
    exit_code, report_data = generate_report(Path("cases/files_changed"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"changed": 1}


def test_changed_lot():
    exit_code, report_data = generate_report(Path("cases/files_changed_lot"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"changed": 1}


def test_changed_mode():
    exit_code, report_data = generate_report(Path("cases/files_changed_mode"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"changed": 1}


def test_changed_size():
    exit_code, report_data = generate_report(Path("cases/files_changed_size"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"changed": 1}


def test_removed():
    exit_code, report_data = generate_report(Path("cases/files_removed"))
    assert exit_code == 1
    assert report_data.has_changes is True
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"deleted": 1}


def test_unchanged():
    exit_code, report_data = generate_report(Path("cases/files_unchanged"))
    assert exit_code == 0
    assert report_data.has_changes is False
    assert {k: v for k, v in report_data.summary.items() if v != 0} == {"unchanged": 1}
