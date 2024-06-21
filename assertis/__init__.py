import os
import tempfile

from assertis.comparison import write_comparison
from assertis.models import Report, report_to_string


class ComparisonException(Exception):
    pass


def compare(expected, actual, output=None, sensitivity=0):
    if output is None:
        output = tempfile.mkdtemp(prefix="assertis_")

    report = write_comparison(expected, actual, output, sensitivity)
    if report.has_changes:
        raise ComparisonException(report_to_string(report, output))
