from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal, Any


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    actual_out_path: Optional[str]
    actual_src_md5: str
    actual_src_path: str
    type: Literal["added"] = "added"


class DeletedFile(BaseFile, extra="forbid"):
    expected_out_path: Optional[str]
    expected_src_path: str
    expected_src_md5: str
    type: Literal["deleted"] = "deleted"


class ChangedFile(BaseFile, extra="forbid"):
    actual_out_path: Optional[str]
    actual_src_md5: str
    actual_src_path: str
    diff_path: Optional[str]
    expected_out_path: Optional[str]
    expected_src_md5: str
    expected_src_path: str
    type: Literal["changed"] = "changed"


class UnchangedFile(BaseFile, extra="forbid"):
    actual_out_path: Optional[str]
    actual_src_md5: str
    actual_src_path: str
    expected_out_path: Optional[str]
    expected_src_md5: str
    expected_src_path: str
    type: Literal["unchanged"] = "unchanged"


class Report(BaseModel, extra="forbid"):
    diff_images: Dict[str, Any] = Field(default_factory=dict)
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))


def report_to_string(report: Report, output: str = None) -> str:
    result = []
    result.append(f"Report has {'changes' if report.has_changes else 'no changes'}")
    result.append("Summary:")
    for key, value in report.summary.items():
        result.append(f"  {key}: {value}")
    result.append("Files:")
    for file in report.files:
        result.append(f"  {file.type}: {file.name} ({', '.join(file.reasons)})")
    if output:
        result.append(f"Comparison results are stored in the directory: {output}")
    return "\n".join(result)
