from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []


class AddedFile(BaseFile, extra="forbid"):
    actual_out_path: Optional[str]
    comparison_result: Literal["added"] = "added"
    actual_src_path: Optional[str] = None


class DeletedFile(BaseFile, extra="forbid"):
    expected_out_path: Optional[str]
    comparison_result: Literal["deleted"] = "deleted"
    expected_src_path: Optional[str] = None


class ChangedFile(BaseFile, extra="forbid"):
    expected_out_path: Optional[str]
    actual_out_path: Optional[str]
    diff_path: Optional[str]
    comparison_result: Literal["changed"] = "changed"
    expected_src_path: Optional[str] = None
    actual_src_path: Optional[str] = None


class UnchangedFile(BaseFile, extra="forbid"):
    expected_out_path: Optional[str]
    actual_out_path: Optional[str]
    comparison_result: Literal["unchanged"] = "unchanged"
    expected_src_path: Optional[str] = None
    actual_src_path: Optional[str] = None


class ReportData(BaseModel, extra="forbid"):
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
