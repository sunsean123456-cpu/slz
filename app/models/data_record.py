"""
数据记录模型（社区达人模块）
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class DataRecord(Base):
    """数据记录表"""
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    community = Column(String(100), nullable=True)  # 社区名称
    data_type = Column(String(50), nullable=False)  # 数据类型：人口/房屋/设施等
    record_count = Column(Integer, default=0)  # 记录数
    valid_count = Column(Integer, default=0)  # 有效记录数
    invalid_count = Column(Integer, default=0)  # 无效记录数
    data = Column(JSON, nullable=True)  # 数据内容
    validation_result = Column(JSON, nullable=True)  # 校验结果
    status = Column(String(20), default="pending")  # pending/validating/validated/entered
    entered_at = Column(DateTime(timezone=True), nullable=True)  # 入表时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataRecord {self.data_type} ({self.community})>"
