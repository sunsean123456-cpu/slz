"""
城市体检路由 - 真实报告审查、图表生成
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.health_report import HealthReport
from app.schemas.health import HealthReportCreate, HealthReportResponse
from app.services.health_engine import health_engine
from app.services.document_parser import document_parser
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 上传目录
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    文件上传接口
    支持：PDF/Word/图片
    """
    try:
        # 生成文件名
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_name = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 检测文件类型
        file_type = document_parser.detect_file_type(file.filename)
        
        return {
            "success": True,
            "file_name": unique_name,
            "file_type": file_type
        }
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def review_report(
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    真实报告审查
    """
    review_result = await health_engine.review_report(content)
    
    return review_result


@router.post("/generate")
async def generate_report(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    生成体检报告
    """
    report_result = await health_engine.generate_report(data)
    
    return report_result


@router.post("/optimize")
async def optimize_report(
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    优化报告
    """
    optimize_result = await health_engine.optimize_report(content)
    
    return optimize_result


@router.post("/charts")
async def generate_charts(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    生成可视化图表
    """
    charts_result = await health_engine.generate_charts(data)
    
    return charts_result


@router.post("/ppt")
async def generate_ppt(
    report_content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    生成汇报 PPT
    """
    ppt_result = await health_engine.generate_ppt(report_content)
    
    return ppt_result


@router.get("/reports")
async def list_reports(
    project_id: int = None,
    year: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    查询体检报告列表
    """
    from sqlalchemy import select
    
    query = select(HealthReport)
    
    if project_id:
        query = query.where(HealthReport.project_id == project_id)
    if year:
        query = query.where(HealthReport.year == year)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return {
        "success": True,
        "reports": [
            {
                "id": report.id,
                "title": report.title,
                "score": report.score,
                "level": report.level,
                "year": report.year,
                "issues": report.issues,
                "suggestions": report.suggestions,
                "charts": report.charts,
                "ppt_url": report.ppt_url,
                "report_url": report.report_url,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ]
    }
