"""
城市体检路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.health_report import HealthReport
from app.schemas.health import HealthReportCreate, HealthReportResponse
from app.schemas.multimodal import MultimodalInput
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=HealthReportResponse)
async def create_health_report(
    data: HealthReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建体检报告
    """
    try:
        report = HealthReport(
            project_id=data.project_id,
            title=data.title,
            year=data.year
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return report
    except Exception as e:
        logger.error(f"创建体检报告失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[HealthReportResponse])
async def list_health_reports(
    project_id: int = None,
    year: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    查询体检报告列表
    """
    query = select(HealthReport)
    
    if project_id:
        query = query.where(HealthReport.project_id == project_id)
    if year:
        query = query.where(HealthReport.year == year)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports


@router.get("/{report_id}", response_model=HealthReportResponse)
async def get_health_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """获取体检报告详情"""
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    return report


@router.delete("/{report_id}")
async def delete_health_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """删除体检报告"""
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    await db.delete(report)
    await db.commit()
    
    return {"success": True, "message": "体检报告已删除"}


@router.post("/{report_id}/review")
async def review_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    审查体检报告
    逐项审查：数据准确性、逻辑一致性、格式规范性
    """
    # 获取体检报告
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    # 调用 AI 服务进行审查
    review_result = await ai_service.analyze_compliance(
        content=report.title,
        policies=[]
    )
    
    # 更新报告
    report.issues = review_result.get("issues", [])
    report.suggestions = review_result.get("suggestions", [])
    
    await db.commit()
    await db.refresh(report)
    
    return {
        "report_id": report_id,
        "review_result": review_result
    }


@router.post("/{report_id}/optimize")
async def optimize_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    优化体检报告
    优化文字表述、数据呈现、图表质量
    """
    # 获取体检报告
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    # 调用 AI 服务进行优化
    optimized_content = await ai_service.optimize_report(
        content=report.title
    )
    
    # 更新报告
    report.suggestions = optimized_content
    
    await db.commit()
    await db.refresh(report)
    
    return {
        "report_id": report_id,
        "optimized_content": optimized_content
    }


@router.post("/{report_id}/generate-charts")
async def generate_charts(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    生成可视化图表
    支持：柱状图、对比图、雷达图、折线图、饼图
    """
    # 获取体检报告
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    # 生成图表数据（实际应调用图表生成服务）
    charts = {
        "bar_chart": {"title": "各维度得分对比", "data": [82.3, 75.8, 71.2, 68.9, 85.1]},
        "radar_chart": {"title": "5 大维度综合评估", "data": [82.3, 75.8, 71.2, 68.9, 85.1]},
        "line_chart": {"title": "关键指标年度趋势", "data": [74.2, 76.1, 78.5]},
        "pie_chart": {"title": "问题类型分布", "data": [35, 25, 20, 20]}
    }
    
    # 更新报告
    report.charts = charts
    
    await db.commit()
    await db.refresh(report)
    
    return {
        "report_id": report_id,
        "charts": charts
    }


@router.post("/{report_id}/generate-ppt")
async def generate_ppt(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    生成汇报 PPT
    12 页标准结构
    """
    # 获取体检报告
    result = await db.execute(
        HealthReport.__table__.select().where(HealthReport.id == report_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")
    
    # 生成 PPT（实际应调用 PPT 生成服务）
    ppt_url = f"/uploads/ppt/{report_id}.pptx"
    
    # 更新报告
    report.ppt_url = ppt_url
    
    await db.commit()
    await db.refresh(report)
    
    return {
        "report_id": report_id,
        "ppt_url": ppt_url,
        "pages": 12,
        "structure": [
            "第 1 页：封面 + 体检概况",
            "第 2 页：综合得分雷达图",
            "第 3-7 页：各维度详细分析",
            "第 8 页：问题清单 + 根因分析",
            "第 9 页：整治方案（优先级矩阵）",
            "第 10 页：年度对比趋势",
            "第 11 页：资金需求 + 部门分工",
            "第 12 页：下一步工作计划"
        ]
    }


async def process_multimodal(input_data: MultimodalInput) -> dict:
    """
    处理多模态输入（城市体检模块）
    
    Args:
        input_data: 多模态输入数据
    
    Returns:
        处理结果
    """
    result = {
        "module": "health",
        "status": "processing",
        "message": "正在处理多模态输入..."
    }
    
    # 处理文本输入
    if input_data.text:
        result["text_input"] = input_data.text
    
    # 处理图片输入
    if input_data.image_url:
        result["image_input"] = input_data.image_url
    
    # 处理文件输入
    if input_data.file_url:
        result["file_input"] = input_data.file_url
    
    # 处理音频输入
    if input_data.audio_url:
        result["audio_input"] = input_data.audio_url
    
    # 处理视频输入
    if input_data.video_url:
        result["video_input"] = input_data.video_url
    
    result["status"] = "completed"
    result["message"] = "多模态输入处理完成"
    
    return result
