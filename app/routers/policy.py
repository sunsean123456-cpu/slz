"""
政策咨询路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.policy import Policy
from app.schemas.policy import PolicyResponse
from app.schemas.multimodal import MultimodalInput
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=PolicyResponse)
async def create_policy(
    title: str,
    content: str = None,
    level: str = None,
    status: str = "active",
    tags: list = None,
    source: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    创建政策法规
    """
    try:
        policy = Policy(
            title=title,
            content=content,
            level=level,
            status=status,
            tags=tags,
            source=source
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        
        return policy
    except Exception as e:
        logger.error(f"创建政策法规失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[PolicyResponse])
async def list_policies(
    level: str = None,
    status: str = None,
    tag: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    查询政策法规列表
    """
    query = select(Policy)
    
    if level:
        query = query.where(Policy.level == level)
    if status:
        query = query.where(Policy.status == status)
    if tag:
        query = query.where(Policy.tags.contains([tag]))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    """获取政策法规详情"""
    result = await db.execute(
        Policy.__table__.select().where(Policy.id == policy_id)
    )
    policy = result.first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="政策法规不存在")
    
    return policy


@router.delete("/{policy_id}")
async def delete_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    """删除政策法规"""
    result = await db.execute(
        Policy.__table__.select().where(Policy.id == policy_id)
    )
    policy = result.first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="政策法规不存在")
    
    await db.delete(policy)
    await db.commit()
    
    return {"success": True, "message": "政策法规已删除"}


@router.post("/analyze")
async def analyze_compliance(
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    合规分析
    分析内容是否符合政策法规
    """
    # 获取所有现行政策法规
    result = await db.execute(
        select(Policy).where(Policy.status == "active")
    )
    policies = result.scalars().all()
    
    # 调用 AI 服务进行合规分析
    analysis_result = await ai_service.analyze_compliance(
        content=content,
        policies=[p.__dict__ for p in policies]
    )
    
    return {
        "content": content,
        "analysis": analysis_result
    }


async def process_multimodal(input_data: MultimodalInput) -> dict:
    """
    处理多模态输入（政策咨询模块）
    
    Args:
        input_data: 多模态输入数据
    
    Returns:
        处理结果
    """
    result = {
        "module": "policy",
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
