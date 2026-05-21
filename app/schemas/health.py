"""
体检报告模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


class HealthReportCreate(BaseModel):
    """体检报告创建"""
    project_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    year: Optional[int] = None


class HealthReportResponse(BaseModel):
    """体检报告响应"""
    id: int
    project_id: Optional[int] = None
    title: str
    score: Optional[Decimal] = None
    level: Optional[str] = None
    year: Optional[int] = None
    issues: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    charts: Optional[Dict[str, Any]] = None
    ppt_url: Optional[str] = None
    report_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
