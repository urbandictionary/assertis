from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal, Any


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_out_path: Optional[str]
    actual_src_path: str
    type: Literal["added"] = "added"


class DeletedFile(BaseFile, extra="forbid"):
    expected_md5: str
    expected_out_path: Optional[str]
    expected_src_path: str
    type: Literal["deleted"] = "deleted"


class ChangedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_out_path: Optional[str]
    actual_src_path: str
    diff_path: Optional[str]
    expected_md5: str
    expected_out_path: Optional[str]
    expected_src_path: str
    type: Literal["changed"] = "changed"


class UnchangedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_out_path: Optional[str]
    actual_src_path: str
    expected_md5: str
    expected_out_path: Optional[str]
    expected_src_path: str
    type: Literal["unchanged"] = "unchanged"


class Report(BaseModel, extra="forbid"):
    outputs: Dict[str, Any] = Field(default_factory=dict)
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))


def report_to_string(report: Report, output: str = None) -> str:
    "Convert the report object to a formatted string."
    result = []
    if report.has_changes:
        summary_parts = [
            f"{value} {key}" for key, value in report.summary.items() if value != 0
        ]
        summary_str = ", ".join(summary_parts)
        result.append(f"Comparison failed ({summary_str}).")
    else:
        result.append("Comparison passed.")
    result.append("\nFiles:")
    for file in report.files:
        result.append(f"  {file.name}: {'; '.join(file.reasons)}")
    if output:
        result.append(f"\nComparison results are stored in the directory: {output}")
    return "\n".join(result)
