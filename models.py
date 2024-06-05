from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from collections import defaultdict


class FileReport(BaseModel):
    name: str
    expected_path: Optional[str]
    actual_path: Optional[str]
    diff: Optional[str]
    comparison_result: str
    reason: str
    expected_abs_path: Optional[str] = None
    actual_abs_path: Optional[str] = None


class ReportData(BaseModel):
    files: List[FileReport] = Field(default_factory=list)
    has_changes: bool = False
    summary: Dict[str, int] = Field(default_factory=lambda: defaultdict(int))
