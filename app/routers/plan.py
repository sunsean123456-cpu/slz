"""
方案评审路由 - 真实 AI 评审
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.plan_review import PlanReview
from app.schemas.plan import PlanReviewCreate, PlanReviewResponse
from app.services.review_engine import review_engine
from app.services.document_parser import document_parser
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 上传目录
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_plan(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传方案文件
    支持：PDF/Word/Excel
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
        
        # 创建评审记录
        review = PlanReview(
            title=file.filename,
            status="uploading",
            file_name=unique_name,
            file_path=file_path,
            file_type=file_type
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        
        return {
            "success": True,
            "review_id": review.id,
            "file_name": unique_name,
            "file_type": file_type
        }
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/parse")
async def parse_plan(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    解析方案文件
    """
    # 获取评审记录
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评审记录不存在")
    
    if not os.path.exists(review.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 解析文件
    parse_result = await document_parser.parse_file(review.file_path, review.file_type)
    
    if "error" in parse_result:
        raise HTTPException(status_code=500, detail=parse_result["error"])
    
    # 更新评审记录
    review.file_content = parse_result.get("text", "")
    review.status = "parsed"
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "success": True,
        "review_id": review_id,
        "parse_result": parse_result
    }


@router.post("/{review_id}/review")
async def review_plan(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    真实 AI 评审方案
    """
    # 获取评审记录
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评审记录不存在")
    
    if not review.file_content:
        raise HTTPException(status_code=400, detail="请先解析文件")
    
    # 更新状态
    review.status = "reviewing"
    await db.commit()
    
    # 调用真实 AI 评审
    review_result = await review_engine.review_plan(
        plan_content=review.file_content,
        plan_type="老旧改造"
    )
    
    if not review_result["success"]:
        raise HTTPException(status_code=500, detail=review_result.get("error", "评审失败"))
    
    # 更新评审结果
    result_data = review_result["review_result"]
    review.score = result_data.get("total_score")
    review.level = result_data.get("level")
    review.dimensions = result_data.get("dimensions")
    review.issues = result_data.get("issues")
    review.suggestions = result_data.get("optimization_plan")
    review.risks = result_data.get("risks")
    review.status = "completed"
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "success": True,
        "review_id": review_id,
        "review_result": result_data
    }


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取评审结果
    """
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评审记录不存在")
    
    return {
        "success": True,
        "review": review
    }


@router.post("/{review_id}/optimize")
async def optimize_plan(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    生成优化方案
    """
    # 获取评审记录
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评审记录不存在")
    
    if not review.suggestions:
        raise HTTPException(status_code=400, detail="请先完成评审")
    
    # 生成优化方案
    optimization_plan = {
        "budget_adjustment": review.suggestions.get("budget_adjustment", ""),
        "schedule_optimization": review.suggestions.get("schedule_optimization", ""),
        "communication_mechanism": review.suggestions.get("communication_mechanism", ""),
        "technical_improvement": review.suggestions.get("technical_improvement", "")
    }
    
    return {
        "success": True,
        "optimization_plan": optimization_plan
    }


@router.post("/{review_id}/export")
async def export_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    导出评审报告
    """
    # 获取评审记录
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评审记录不存在")
    
    # 生成 PDF 报告（实际项目中应使用报告生成库）
    report_content = f"""
    # 方案评审报告
    
    ## 基本信息
    - 方案名称：{review.title}
    - 评审时间：{review.created_at}
    - 综合评分：{review.score}
    - 评审等级：{review.level}
    
    ## 五维评分
    | 维度 | 得分 | 权重 | 加权分 |
    |------|------|------|--------|
    | 政策合规性 | {review.dimensions.get('policy_compliance', {}).get('score', 'N/A')} | 25% | {review.dimensions.get('policy_compliance', {}).get('weighted_score', 'N/A')} |
    | 技术可行性 | {review.dimensions.get('technical_feasibility', {}).get('score', 'N/A')} | 25% | {review.dimensions.get('technical_feasibility', {}).get('weighted_score', 'N/A')} |
    | 经济合理性 | {review.dimensions.get('economic_rationality', {}).get('score', 'N/A')} | 20% | {review.dimensions.get('economic_rationality', {}).get('weighted_score', 'N/A')} |
    | 社会可接受度 | {review.dimensions.get('social_acceptance', {}).get('score', 'N/A')} | 15% | {review.dimensions.get('social_acceptance', {}).get('weighted_score', 'N/A')} |
    | 实施可操作性 | {review.dimensions.get('implementation_operability', {}).get('score', 'N/A')} | 15% | {review.dimensions.get('implementation_operability', {}).get('weighted_score', 'N/A')} |
    
    ## 发现问题
    {chr(10).join([f"- {issue.get('title', '')}: {issue.get('description', '')}" for issue in review.issues or []])}
    
    ## 优化建议
    {chr(10).join([f"- {suggestion}" for suggestion in review.suggestions.values() if suggestion])}
    
    ## 风险预警
    {chr(10).join([f"- [{risk.get('level', '')}] {risk.get('type', '')}: {risk.get('description', '')}" for risk in review.risks or []])}
    """
    
    return {
        "success": True,
        "report_content": report_content
    }
