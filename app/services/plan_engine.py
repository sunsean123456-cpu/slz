"""
方案评审引擎 - 真实 AI 评审
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.plan_review import PlanReview
from app.services.review_engine import review_engine

logger = logging.getLogger(__name__)


class PlanEngine:
    """方案评审引擎"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    async def review_plan(self, plan_content: str, plan_type: str = "老旧改造") -> Dict[str, Any]:
        """
        真实方案评审
        
        Args:
            plan_content: 方案内容
            plan_type: 方案类型
        
        Returns:
            评审结果
        """
        try:
            # 调用真实评审引擎
            result = await review_engine.review_plan(plan_content, plan_type)
            
            if result["success"]:
                return {
                    "success": True,
                    "review_result": result["review_result"]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "评审失败")
                }
        except Exception as e:
            logger.error(f"方案评审失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_optimization(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成优化方案
        
        Args:
            review_result: 评审结果
        
        Returns:
            优化方案
        """
        try:
            prompt = f"""
            请根据以下评审结果生成优化方案：
            
            {json.dumps(review_result, ensure_ascii=False, indent=2)}
            
            优化方案应包含：
            1. 预算调整建议
            2. 进度优化建议
            3. 居民沟通机制
            4. 技术改进建议
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的方案优化专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return {
                "success": True,
                "optimization_plan": json.loads(response.choices[0].message.content)
            }
        except Exception as e:
            logger.error(f"生成优化方案失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_risk_warning(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成风险预警
        
        Args:
            review_result: 评审结果
        
        Returns:
            风险预警
        """
        try:
            risks = review_result.get("risks", [])
            
            return {
                "success": True,
                "risks": risks
            }
        except Exception as e:
            logger.error(f"生成风险预警失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def insert_template(self, template_type: str) -> Dict[str, Any]:
        """
        插入评审意见模板
        
        Args:
            template_type: 模板类型
        
        Returns:
            模板内容
        """
        templates = {
            "budget_adjustment": {
                "title": "预算调整建议",
                "content": "建议调整拆迁补偿预算，上调至市场均价水平，并增加过渡期安置补贴。"
            },
            "schedule_optimization": {
                "title": "进度优化建议",
                "content": "建议增加雨季缓冲期，调整关键路径，采用装配式施工工艺缩短工期。"
            },
            "communication_mechanism": {
                "title": "居民沟通建议",
                "content": "建议建立'一户一策'沟通机制，设立居民咨询服务中心，加强政策宣传。"
            },
            "technical_improvement": {
                "title": "技术改进建议",
                "content": "建议采用装配式施工工艺，提高施工效率，缩短工期 20%。"
            },
            "legal_risk": {
                "title": "法律风险提示",
                "content": "注意听证会通知时间不足 7 日的法律风险，建议提前 15 日通知。"
            }
        }
        
        template = templates.get(template_type, {})
        
        return {
            "success": True,
            "template": template
        }


# 全局方案引擎实例
plan_engine = PlanEngine()
