"""
政策法规模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Policy(Base):
    """政策法规表"""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    level = Column(String(20), nullable=False)  # 法律/行政法规/地方性法规/部门规章
    status = Column(String(20), default="active")  # active/expired/abolished
    tags = Column(JSON, nullable=True)  # 标签列表
    source = Column(String(255), nullable=True)  # 来源
    effective_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Policy {self.title}>"
