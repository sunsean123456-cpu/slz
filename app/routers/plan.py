"""
方案评审路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.plan_review import PlanReview
from app.schemas.plan import PlanReviewCreate, PlanReviewResponse
from app.schemas.multimodal import MultimodalInput
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=PlanReviewResponse)
async def create_plan_review(
    data: PlanReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建方案评审
    """
    try:
        review = PlanReview(
            project_id=data.project_id,
            title=data.title
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        
        return review
    except Exception as e:
        logger.error(f"创建方案评审失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[PlanReviewResponse])
async def list_plan_reviews(
    project_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    查询方案评审列表
    """
    query = select(PlanReview)
    
    if project_id:
        query = query.where(PlanReview.project_id == project_id)
    if status:
        query = query.where(PlanReview.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return reviews


@router.get("/{review_id}", response_model=PlanReviewResponse)
async def get_plan_review(review_id: int, db: AsyncSession = Depends(get_db)):
    """获取方案评审详情"""
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    return review


@router.delete("/{review_id}")
async def delete_plan_review(review_id: int, db: AsyncSession = Depends(get_db)):
    """删除方案评审"""
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    await db.delete(review)
    await db.commit()
    
    return {"success": True, "message": "方案评审已删除"}


@router.post("/{review_id}/review")
async def review_plan(review_id: int, db: AsyncSession = Depends(get_db)):
    """
    评审方案
    5 大维度评分、问题清单、优化建议
    """
    # 获取方案评审
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    # 调用 AI 服务进行评审
    review_result = await ai_service.review_plan(
        content=review.title
    )
    
    # 更新评审
    review.score = review_result.get("score")
    review.level = review_result.get("level")
    review.dimensions = review_result.get("dimensions")
    review.issues = review_result.get("issues")
    review.suggestions = review_result.get("suggestions")
    review.risks = review_result.get("risks")
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "review_id": review_id,
        "review_result": review_result
    }


@router.post("/{review_id}/optimize")
async def optimize_plan(review_id: int, db: AsyncSession = Depends(get_db)):
    """
    优化方案
    生成优化方案
    """
    # 获取方案评审
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    # 调用 AI 服务进行优化
    optimized_content = await ai_service.optimize_report(
        content=review.title
    )
    
    # 更新评审
    review.suggestions = optimized_content
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "review_id": review_id,
        "optimized_content": optimized_content
    }


@router.post("/{review_id}/approve")
async def approve_plan(review_id: int, db: AsyncSession = Depends(get_db)):
    """
    评审通过
    """
    # 获取方案评审
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    # 更新状态
    review.status = "approved"
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "review_id": review_id,
        "status": "approved",
        "message": "评审通过！方案已确认，可进入实施阶段。"
    }


@router.post("/{review_id}/reject")
async def reject_plan(review_id: int, db: AsyncSession = Depends(get_db)):
    """
    评审不通过
    """
    # 获取方案评审
    result = await db.execute(
        PlanReview.__table__.select().where(PlanReview.id == review_id)
    )
    review = result.first()
    
    if not review:
        raise HTTPException(status_code=404, detail="方案评审不存在")
    
    # 更新状态
    review.status = "rejected"
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "review_id": review_id,
        "status": "rejected",
        "message": "评审不通过！请根据优化建议修改后重新提交。"
    }


async def process_multimodal(input_data: MultimodalInput) -> dict:
    """
    处理多模态输入（方案评审模块）
    
    Args:
        input_data: 多模态输入数据
    
    Returns:
        处理结果
    """
    result = {
        "module": "plan",
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
