from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from collections import defaultdict
from typing import Literal


class FileReport(BaseModel):
    name: str
    output_expected_path: Optional[str]
    output_actual_path: Optional[str]
    diff_path: Optional[str]
    comparison_result: Literal["added", "deleted", "changed", "unchanged"]
    reason: str
    orginal_expected_path: Optional[str] = None
    orginal_actual_path: Optional[str] = None


class ReportData(BaseModel):
    files: List[FileReport] = Field(default_factory=list)
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
