from assertis.comparison import run_comparison
from assertis.models import report_to_string, Report


class ComparisonException(Exception):
    def __init__(self, report: Report):
        self.report = report
        super().__init__(report_to_string(report))


def compare(expected, actual, output, sensitivity=0):
    report = run_comparison(expected, actual, output, sensitivity)
    if report.has_changes:
        raise ComparisonException(report)
