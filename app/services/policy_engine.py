"""
政策咨询引擎 - 真实合规审查、判例查询
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.policy import Policy
from app.services.document_parser import document_parser

logger = logging.getLogger(__name__)


class PolicyEngine:
    """政策咨询引擎"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    async def compliance_review(self, content: str) -> Dict[str, Any]:
        """
        真实合规审查
        
        Args:
            content: 审查内容
        
        Returns:
            审查结果
        """
        try:
            # 1. 检索相关法规
            policies = await self._search_policies(content)
            
            # 2. 使用 AI 进行合规分析
            review_result = await self._analyze_compliance(content, policies)
            
            # 3. 生成检查清单
            checklist = await self._generate_checklist(review_result)
            
            return {
                "success": True,
                "conclusion": review_result.get("conclusion", "合规"),
                "legal_basis": review_result.get("legal_basis", []),
                "checklist": checklist,
                "steps": review_result.get("steps", []),
                "risks": review_result.get("risks", [])
            }
            
        except Exception as e:
            logger.error(f"合规审查失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _search_policies(self, content: str) -> List[Dict[str, Any]]:
        """检索相关法规"""
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                
                # 使用 AI 生成搜索关键词
                prompt = f"""
                请根据以下内容生成搜索关键词：
                
                {content}
                
                请返回 3-5 个关键词，用于检索相关法规。
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位专业的法律检索专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                
                keywords = json.loads(response.choices[0].message.content)
                
                # 检索数据库
                query = select(Policy)
                for keyword in keywords:
                    query = query.where(Policy.title.contains(keyword))
                
                result = await session.execute(query)
                policies = result.scalars().all()
                
                return [
                    {
                        "id": policy.id,
                        "title": policy.title,
                        "content": policy.content,
                        "level": policy.level,
                        "status": policy.status
                    }
                    for policy in policies
                ]
        except Exception as e:
            logger.error(f"法规检索失败：{str(e)}")
            return []
    
    async def _analyze_compliance(self, content: str, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI 合规分析"""
        prompt = f"""
        请对以下内容进行合规分析：
        
        内容：
        {content}
        
        相关法规：
        {json.dumps(policies, ensure_ascii=False, indent=2)}
        
        请返回以下格式的 JSON：
        {{
            "conclusion": "合规/不合规/部分合规",
            "legal_basis": ["法规 1", "法规 2"],
            "steps": ["处置步骤 1", "处置步骤 2"],
            "risks": ["风险点 1", "风险点 2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的法律顾问，擅长合规审查。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"合规分析失败：{str(e)}")
            return {"conclusion": "分析失败", "error": str(e)}
    
    async def _generate_checklist(self, review_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成检查清单"""
        checklist = []
        
        # 基于审查结果生成检查项
        if review_result.get("legal_basis"):
            for basis in review_result["legal_basis"]:
                checklist.append({
                    "item": f"确认{basis}合规",
                    "status": "pending",
                    "detail": ""
                })
        
        if review_result.get("risks"):
            for risk in review_result["risks"]:
                checklist.append({
                    "item": f"处理风险：{risk}",
                    "status": "pending",
                    "detail": ""
                })
        
        return checklist
    
    async def search_cases(self, query: str) -> Dict[str, Any]:
        """
        真实判例查询
        
        Args:
            query: 查询内容
        
        Returns:
            判例结果
        """
        try:
            # 使用 AI 进行判例检索
            prompt = f"""
            请根据以下查询检索相关判例：
            
            {query}
            
            请返回 3-5 个最相关的判例，包含：
            - 判例编号
            - 案件名称
            - 裁判结果
            - 相似原因
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的法律判例检索专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"判例查询失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_opinion(self, content: str) -> Dict[str, Any]:
        """
        生成书面咨询意见
        
        Args:
            content: 咨询内容
        
        Returns:
            咨询意见
        """
        try:
            prompt = f"""
            请根据以下内容生成书面咨询意见：
            
            {content}
            
            咨询意见应包含：
            1. 咨询事项概述
            2. 政策法规依据
            3. 合规性分析
            4. 结论与建议
            5. 风险提示
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的法律顾问，擅长撰写咨询意见。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return {
                "success": True,
                "opinion": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"生成咨询意见失败：{str(e)}")
            return {"success": False, "error": str(e)}


# 全局政策引擎实例
policy_engine = PolicyEngine()
