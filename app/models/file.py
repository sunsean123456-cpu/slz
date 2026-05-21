"""
文件模型
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class File(Base):
    """文件表"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # excel/csv/pdf/word/image/audio/video
    size = Column(BigInteger, nullable=False)
    url = Column(String(500), nullable=False)
    metadata = Column(JSON, nullable=True)  # 文件元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<File {self.name} ({self.file_type})>"
