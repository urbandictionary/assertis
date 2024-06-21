from collections import defaultdict
from typing import List, Literal, Optional, Union
from pathlib import Path

from PIL import Image
from pydantic import BaseModel, Field


class Output(BaseModel):
    filename: str
    content: Union[Image.Image, Path]


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_file: str
    type: Literal["added"] = "added"


class DeletedFile(BaseFile, extra="forbid"):
    expected_md5: str
    type: Literal["deleted"] = "deleted"


class ChangedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_file: str
    diff_file: Optional[str]
    expected_md5: str
    expected_file: str
    type: Literal["changed"] = "changed"


class UnchangedFile(BaseFile, extra="forbid"):
    actual_md5: str
    actual_file: str
    expected_md5: str
    expected_file: str
    type: Literal["unchanged"] = "unchanged"


class Report(BaseModel, extra="forbid"):
    outputs: List[Output] = Field(default_factory=list)
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))


def report_to_string(report: Report, report_dir: str = None) -> str:
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
    if report_dir:
        result.append(f"\nReport is in the directory: {report_dir}")
    return "\n".join(result)
