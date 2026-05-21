"""
项目模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    """项目创建"""
    name: str = Field(..., min_length=1, max_length=100)
    project_type: str = Field(..., pattern="^(data|policy|health|plan)$")
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    name: str
    project_type: str
    status: str
    description: Optional[str] = None
    user_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
