import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from assertis.cli import assertis  # Replace with the actual name of your script module
from assertis.models import Report


def generate_report(cases_dir):
    cases_path = Path(cases_dir)
    expected_dir = cases_path / "expected"
    actual_dir = cases_path / "actual"

    with tempfile.TemporaryDirectory() as temp_dir:
        report_dir = Path(temp_dir)

        runner = CliRunner()
        result = runner.invoke(
            assertis,
            [
                "compare",
                str(expected_dir),
                str(actual_dir),
                str(report_dir),
                "--sensitivity",
                "0",
            ],
            catch_exceptions=False,  # Ensure that exceptions are not caught and displayed in stderr
        )

        report_path = report_dir / "report.json"
        if not report_path.exists():
            raise FileNotFoundError(f"report.json not found in {report_dir}")

        with open(report_path, "r") as report_file:
            report = Report(**json.load(report_file))

    return result.exit_code, report


def test_empty():
    exit_code, report = generate_report(Path("testcases/empty"))
    assert exit_code == 0
    assert report.has_changes is False
    assert {k: v for k, v in report.summary.items() if v != 0} == {}


def test_added():
    exit_code, report = generate_report(Path("testcases/files_added"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"added": 1}


def test_changed():
    exit_code, report = generate_report(Path("testcases/files_changed"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"changed": 1}


def test_changed_lot():
    exit_code, report = generate_report(Path("testcases/files_changed_lot"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"changed": 1}


def test_changed_mode():
    exit_code, report = generate_report(Path("testcases/files_changed_mode"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"changed": 1}


def test_changed_size():
    exit_code, report = generate_report(Path("testcases/files_changed_size"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"changed": 1}


def test_removed():
    exit_code, report = generate_report(Path("testcases/files_removed"))
    assert exit_code == 1
    assert report.has_changes is True
    assert {k: v for k, v in report.summary.items() if v != 0} == {"deleted": 1}


def test_unchanged():
    exit_code, report = generate_report(Path("testcases/files_unchanged"))
    assert exit_code == 0
    assert report.has_changes is False
    assert {k: v for k, v in report.summary.items() if v != 0} == {"unchanged": 1}
