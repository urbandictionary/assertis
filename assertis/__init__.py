import os
import tempfile
from assertis.comparison import run_comparison
from assertis.models import report_to_string, Report


class ComparisonException(Exception):
    pass


def compare(expected, actual, output=None, sensitivity=0):
    if output is None:
        output = tempfile.mkdtemp(prefix="assertis_")

    report = run_comparison(expected, actual, output, sensitivity)
    if report.has_changes:
        raise ComparisonException(report_to_string(report))

    print(f"Comparison results are stored in the directory: {output}")
