from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal, Any


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    path_out_actual: Optional[str]
    path_src_actual: str
    md5_src_actual: str
    type: Literal["added"] = "added"


class DeletedFile(BaseFile, extra="forbid"):
    path_out_expected: Optional[str]
    path_src_expected: str
    md5_src_expected: str
    type: Literal["deleted"] = "deleted"


class ChangedFile(BaseFile, extra="forbid"):
    diff_path: Optional[str]
    path_out_actual: Optional[str]
    path_out_expected: Optional[str]
    path_src_actual: str
    md5_src_actual: str
    path_src_expected: str
    md5_src_expected: str
    type: Literal["changed"] = "changed"


class UnchangedFile(BaseFile, extra="forbid"):
    path_out_actual: Optional[str]
    path_out_expected: Optional[str]
    path_src_actual: str
    md5_src_actual: str
    path_src_expected: str
    md5_src_expected: str
    type: Literal["unchanged"] = "unchanged"


class Report(BaseModel, extra="forbid"):
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
    diff_images: Dict[str, Any] = Field(default_factory=dict)


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
