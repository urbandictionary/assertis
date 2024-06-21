from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal


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


class ReportData(BaseModel, extra="forbid"):
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
