"""
政策法规模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PolicyResponse(BaseModel):
    """政策法规响应"""
    id: int
    title: str
    content: Optional[str] = None
    level: str
    status: str
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    effective_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
