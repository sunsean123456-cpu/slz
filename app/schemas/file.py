"""
文件模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FileResponse(BaseModel):
    """文件响应"""
    id: int
    project_id: Optional[int] = None
    name: str
    original_name: str
    file_type: str
    size: int
    url: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
