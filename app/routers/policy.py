"""
政策咨询路由 - 真实合规审查、判例查询
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.policy import Policy
from app.schemas.policy import PolicyResponse
from app.services.policy_engine import policy_engine
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


@router.post("/compliance")
async def compliance_review(
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    真实合规审查
    """
    review_result = await policy_engine.compliance_review(content)
    
    return review_result


@router.post("/cases")
async def search_cases(
    query: str,
    db: AsyncSession = Depends(get_db)
):
    """
    真实判例查询
    """
    cases_result = await policy_engine.search_cases(query)
    
    return cases_result


@router.post("/opinion")
async def generate_opinion(
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    生成书面咨询意见
    """
    opinion_result = await policy_engine.generate_opinion(content)
    
    return opinion_result


@router.get("/policies")
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
    from sqlalchemy import select
    
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
    
    return {
        "success": True,
        "policies": [
            {
                "id": policy.id,
                "title": policy.title,
                "content": policy.content,
                "level": policy.level,
                "status": policy.status,
                "tags": policy.tags,
                "source": policy.source
            }
            for policy in policies
        ]
    }
