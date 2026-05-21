"""
方案评审模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class PlanReview(Base):
    """方案评审表"""
    __tablename__ = "plan_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=True)
    level = Column(String(20), nullable=True)
    dimensions = Column(JSON, nullable=True)
    issues = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    risks = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")
    review_url = Column(String(500), nullable=True)
    
    # 文件相关
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(20), nullable=True)
    file_content = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlanReview {self.title}>"
