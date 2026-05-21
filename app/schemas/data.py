"""
数据记录模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DataRecordCreate(BaseModel):
    """数据记录创建"""
    project_id: Optional[int] = None
    file_id: Optional[int] = None
    community: Optional[str] = Field(None, max_length=100)
    data_type: str = Field(..., min_length=1, max_length=50)
    data: Dict[str, Any] = Field(...)  # 数据内容


class DataRecordResponse(BaseModel):
    """数据记录响应"""
    id: int
    project_id: Optional[int] = None
    file_id: Optional[int] = None
    community: Optional[str] = None
    data_type: str
    record_count: int
    valid_count: int
    invalid_count: int
    data: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    status: str
    entered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
