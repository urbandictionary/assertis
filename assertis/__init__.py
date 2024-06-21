import tempfile
import shutil
from assertis.comparison import run_comparison
from assertis.models import report_to_string, Report


class ComparisonException(Exception):
    def __init__(self, report: Report):
        self.report = report
        super().__init__(report_to_string(report))


def compare(expected, actual, output=None, sensitivity=0):
    if output is None:
        output = tempfile.mkdtemp()
    report = run_comparison(expected, actual, output, sensitivity)
    if report.has_changes:
        raise ComparisonException(report)
    # Ensure the temporary directory is preserved after execution
    shutil.copytree(output, output + "_preserved")
