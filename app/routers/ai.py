"""
AI 服务路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.multimodal import MultimodalInput
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    messages: list
):
    """
    AI 对话
    """
    try:
        response = await ai_service.chat(messages)
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"AI 对话失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance")
async def analyze_compliance(
    content: str
):
    """
    合规分析
    """
    try:
        result = await ai_service.analyze_compliance(
            content=content,
            policies=[]
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"合规分析失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def review_plan(
    content: str
):
    """
    方案评审
    """
    try:
        result = await ai_service.review_plan(
            content=content
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"方案评审失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_report(
    data: dict,
    report_type: str = "health"
):
    """
    报告生成
    """
    try:
        response = await ai_service.generate_report(
            data=data,
            report_type=report_type
        )
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"报告生成失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_report(
    content: str
):
    """
    报告优化
    """
    try:
        response = await ai_service.optimize_report(
            content=content
        )
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        logger.error(f"报告优化失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
