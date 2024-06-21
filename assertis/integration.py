import os
from assertis.comparison import run_comparison
from assertis.models import report_to_string, Report

class ComparisonException(Exception):
    def __init__(self, report: Report):
        self.report = report
        super().__init__(report_to_string(report))

def compare_and_raise(expected, actual, output, sensitivity=0):
    has_changes = run_comparison(expected, actual, output, sensitivity)
    if has_changes:
        with open(os.path.join(output, "report.json"), "r") as json_file:
            report_data = json.load(json_file)
            report = Report(**report_data)
            raise ComparisonException(report)
