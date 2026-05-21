"""
方案评审模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, JSON
from sqlalchemy.sql import func
from app.database import Base


class PlanReview(Base):
    """方案评审表"""
    __tablename__ = "plan_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=True)  # 综合评分
    level = Column(String(20), nullable=True)  # 优秀/良好/合格/不合格
    dimensions = Column(JSON, nullable=True)  # 各维度评分
    issues = Column(JSON, nullable=True)  # 问题清单
    suggestions = Column(JSON, nullable=True)  # 优化建议
    risks = Column(JSON, nullable=True)  # 风险预警
    status = Column(String(20), default="pending")  # pending/approved/rejected
    review_url = Column(String(500), nullable=True)  # 评审报告 URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlanReview {self.title}>"
