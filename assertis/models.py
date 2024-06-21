from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from collections import defaultdict
from typing import Literal


class BaseFile(BaseModel, extra="forbid"):
    name: str
    reasons: List[str] = []
    name: str
    reasons: List[str] = []

class AddedFile(BaseFile, extra="forbid"):
    name: str
    output_expected_path: Optional[str] = None
    output_actual_path: Optional[str]
    diff_path: Optional[str] = None
    comparison_result: Literal["added"] = "added"
    original_expected_path: Optional[str] = None
    original_actual_path: Optional[str] = None


class DeletedFile(BaseFile, extra="forbid"):
    output_expected_path: Optional[str]
    output_actual_path: Optional[str] = None
    diff_path: Optional[str] = None
    comparison_result: Literal["deleted"] = "deleted"
    original_expected_path: Optional[str] = None
    original_actual_path: Optional[str] = None


class ChangedFile(BaseFile, extra="forbid"):
    output_expected_path: Optional[str]
    output_actual_path: Optional[str]
    diff_path: Optional[str]
    comparison_result: Literal["changed"] = "changed"
    reasons: List[str]
    original_expected_path: Optional[str] = None
    original_actual_path: Optional[str] = None


class UnchangedFile(BaseFile, extra="forbid"):
    output_expected_path: Optional[str]
    output_actual_path: Optional[str]
    diff_path: Optional[str] = None
    comparison_result: Literal["unchanged"] = "unchanged"
    original_expected_path: Optional[str] = None
    original_actual_path: Optional[str] = None


class ReportData(BaseModel, extra="forbid"):
    files: List[Union[AddedFile, DeletedFile, ChangedFile, UnchangedFile]] = Field(
        default_factory=list
    )
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))