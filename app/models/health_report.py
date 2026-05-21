"""
体检报告模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, JSON
from sqlalchemy.sql import func
from app.database import Base


class HealthReport(Base):
    """体检报告表"""
    __tablename__ = "health_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=True)  # 综合得分
    level = Column(String(10), nullable=True)  # A/B+/B/C
    year = Column(Integer, nullable=True)  # 年份
    issues = Column(JSON, nullable=True)  # 问题清单
    suggestions = Column(JSON, nullable=True)  # 优化建议
    charts = Column(JSON, nullable=True)  # 图表数据
    ppt_url = Column(String(500), nullable=True)  # PPT 文件 URL
    report_url = Column(String(500), nullable=True)  # 报告文件 URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HealthReport {self.title}>"
