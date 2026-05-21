"""
多模态输入模式
"""
from pydantic import BaseModel, Field
from typing import Optional


class MultimodalInput(BaseModel):
    """多模态输入"""
    text: Optional[str] = None  # 文字输入
    image_url: Optional[str] = None  # 图片 URL
    file_url: Optional[str] = None  # 文件 URL（PPT/PDF/Excel 等）
    audio_url: Optional[str] = None  # 音频 URL
    video_url: Optional[str] = None  # 视频 URL
    module: str = Field(..., pattern="^(data|policy|health|plan)$")  # 目标模块
    query: str = Field(..., min_length=1)  # 用户查询/指令
