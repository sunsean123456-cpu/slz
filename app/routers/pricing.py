"""
收费/会员路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 定价方案数据（实际应从数据库读取）
PRICING_PLANS = [
    {
        "id": 1,
        "name": "免费体验版",
        "price": 0,
        "period": "月",
        "features": [
            "基础功能体验",
            "每月 10 次 AI 对话",
            "基础数据核验",
            "标准报告模板"
        ],
        "is_popular": False
    },
    {
        "id": 2,
        "name": "专业版会员",
        "price": 99,
        "period": "月",
        "features": [
            "全部功能解锁",
            "每月 500 次 AI 对话",
            "高级数据核验 + 批量处理",
            "定制化报告 + PPT 生成",
            "优先客服支持"
        ],
        "is_popular": True
    },
    {
        "id": 3,
        "name": "企业版",
        "price": 999,
        "period": "月",
        "features": [
            "专业版全部功能",
            "无限 AI 对话次数",
            "API 接口接入",
            "私有化部署选项",
            "专属客户经理"
        ],
        "is_popular": False
    },
    {
        "id": 4,
        "name": "按量计费",
        "price": 0.1,
        "period": "次",
        "features": [
            "按需购买，灵活使用",
            "单次 AI 对话/报告生成",
            "无月费压力",
            "适合低频使用用户"
        ],
        "is_popular": False
    }
]


@router.get("/plans")
async def get_pricing_plans():
    """获取所有定价方案"""
    return {
        "success": True,
        "plans": PRICING_PLANS
    }


@router.get("/compare")
async def compare_plans():
    """获取功能对比表"""
    comparison = {
        "features": [
            {"name": "AI 对话次数", "free": "10 次/月", "pro": "500 次/月", "enterprise": "无限"},
            {"name": "数据核验", "free": "基础", "pro": "高级", "enterprise": "高级 + 批量"},
            {"name": "报告生成", "free": "标准模板", "pro": "定制化", "enterprise": "定制化 + API"},
            {"name": "客服支持", "free": "自助", "pro": "优先", "enterprise": "专属经理"},
            {"name": "API 接入", "free": "❌", "pro": "❌", "enterprise": "✅"},
            {"name": "私有化部署", "free": "❌", "pro": "❌", "enterprise": "✅"}
        ]
    }
    return {
        "success": True,
        "comparison": comparison
    }


@router.post("/subscribe/{plan_id}")
async def subscribe_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """
    订阅定价方案
    """
    # 查找方案
    plan = next((p for p in PRICING_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="定价方案不存在")
    
    # 实际项目中应创建订阅记录、调用支付接口等
    return {
        "success": True,
        "message": f"已订阅 {plan['name']}，等待支付完成",
        "plan": plan
    }


@router.post("/contact")
async def contact_sales(
    name: str,
    company: str,
    phone: str,
    email: str = None,
    message: str = None
):
    """
    联系销售（企业版咨询）
    """
    # 实际项目中应发送邮件或保存线索
    logger.info(f"销售线索：{name} - {company} - {phone}")
    
    return {
        "success": True,
        "message": "咨询已提交，我们的客户经理将在 24 小时内联系您"
    }
