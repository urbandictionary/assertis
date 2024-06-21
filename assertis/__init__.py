import os
import tempfile

from assertis.comparison import write_comparison
from assertis.models import Report, report_to_string


class ComparisonException(Exception):
    pass


def compare(expected_dir, actual_dir, report_dir=None, sensitivity=0):
    if report_dir is None:
        report_dir = tempfile.mkdtemp(prefix="assertis_")

    report = write_comparison(expected_dir, actual_dir, report_dir, sensitivity)
    if report.has_changes:
        raise ComparisonException(report_to_string(report, report_dir))
