from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal, Any


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    path_out_actual: Optional[str]
    comparison_result: Literal["added"] = "added"
    path_src_actual: Optional[str] = None


class DeletedFile(BaseFile, extra="forbid"):
    path_out_expected: Optional[str]
    comparison_result: Literal["deleted"] = "deleted"
    path_src_expected: Optional[str] = None


class ChangedFile(BaseFile, extra="forbid"):
    path_out_expected: Optional[str]
    path_out_actual: Optional[str]
    diff_path: Optional[str]
    comparison_result: Literal["changed"] = "changed"
    path_src_expected: Optional[str] = None
    path_src_actual: Optional[str] = None


class UnchangedFile(BaseFile, extra="forbid"):
    path_out_expected: Optional[str]
    path_out_actual: Optional[str]
    comparison_result: Literal["unchanged"] = "unchanged"
    path_src_expected: Optional[str] = None
    path_src_actual: Optional[str] = None


class DisplayData(BaseModel, extra="forbid"):
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
    diff_images: Dict[str, Any] = Field(default_factory=dict)


class FullData(BaseModel, extra="forbid"):
    display_data: DisplayData = DisplayData()


def display_data_to_string(display_data: DisplayData) -> str:
    result = []
    result.append(
        f"Report has {'changes' if display_data.has_changes else 'no changes'}"
    )
    result.append("Summary:")
    for key, value in display_data.summary.items():
        result.append(f"  {key}: {value}")
    result.append("Files:")
    for file in display_data.files:
        result.append(
            f"{file.comparison_result}: {file.name} ({', '.join(file.reasons)})"
        )
    return "\n".join(result)
