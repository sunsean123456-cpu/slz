"""
方案评审模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


class PlanReviewCreate(BaseModel):
    """方案评审创建"""
    project_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)


class PlanReviewResponse(BaseModel):
    """方案评审响应"""
    id: int
    project_id: Optional[int] = None
    title: str
    score: Optional[Decimal] = None
    level: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    risks: Optional[List[Dict[str, Any]]] = None
    status: str
    review_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
