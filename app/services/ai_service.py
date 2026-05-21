"""
AI 服务
集成 LLM 推理、RAG 检索、向量检索
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        LLM 对话
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数（0-1）
        
        Returns:
            AI 回复文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 对话失败：{str(e)}")
            return f"AI 服务异常：{str(e)}"
    
    async def analyze_compliance(self, content: str, policies: List[Dict]) -> Dict[str, Any]:
        """
        合规分析
        
        Args:
            content: 待分析内容
            policies: 相关政策法规列表
        
        Returns:
            合规分析结果
        """
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
            "checklist": [
                {{"item": "检查项", "status": "✅/⚠️/❌", "detail": "说明"}},
                ...
            ],
            "steps": ["处置步骤 1", "处置步骤 2", ...],
            "risks": ["风险点 1", "风险点 2", ...]
        }}
        """
        
        try:
            response = await self.chat([{"role": "user", "content": prompt}])
            # 解析 JSON 响应
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"合规分析失败：{str(e)}")
            return {"error": str(e)}
    
    async def review_plan(self, content: str) -> Dict[str, Any]:
        """
        方案评审
        
        Args:
            content: 方案内容
        
        Returns:
            评审结果
        """
        prompt = f"""
        请对以下方案进行评审：
        
        方案内容：
        {content}
        
        请从以下维度评分（满分 100 分）：
        1. 政策合规性（权重 25%）
        2. 技术可行性（权重 25%）
        3. 经济合理性（权重 20%）
        4. 社会可接受度（权重 15%）
        5. 实施可操作性（权重 15%）
        
        请返回以下格式的 JSON：
        {{
            "score": 82.5,
            "level": "良好",
            "dimensions": {
                "政策合规性": 88,
                "技术可行性": 85,
                "经济合理性": 78,
                "社会可接受度": 80,
                "实施可操作性": 82
            },
            "issues": ["问题 1", "问题 2", ...],
            "suggestions": ["建议 1", "建议 2", ...],
            "risks": [
                {{"level": "高/中/低", "type": "风险类型", "detail": "风险描述", "suggestion": "应对建议"}},
                ...
            ]
        }}
        """
        
        try:
            response = await self.chat([{"role": "user", "content": prompt}])
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"方案评审失败：{str(e)}")
            return {"error": str(e)}
    
    async def generate_report(self, data: Dict[str, Any], report_type: str = "health") -> str:
        """
        报告生成
        
        Args:
            data: 数据内容
            report_type: 报告类型（health/plan/policy）
        
        Returns:
            报告内容
        """
        prompt = f"""
        请根据以下数据生成{report_type}报告：
        
        数据：
        {json.dumps(data, ensure_ascii=False, indent=2)}
        
        请生成结构化的报告内容，包含：
        1. 总体概况
        2. 详细分析
        3. 问题诊断
        4. 整治建议
        5. 趋势预测
        """
        
        try:
            response = await self.chat([{"role": "user", "content": prompt}])
            return response
        except Exception as e:
            logger.error(f"报告生成失败：{str(e)}")
            return f"报告生成失败：{str(e)}"
    
    async def optimize_report(self, content: str) -> str:
        """
        报告优化
        
        Args:
            content: 原始报告内容
        
        Returns:
            优化后的报告内容
        """
        prompt = f"""
        请优化以下报告内容，使其更专业、更具体、更具可操作性：
        
        原始报告：
        {content}
        
        优化要求：
        1. 文字表述更精准（避免模糊描述）
        2. 数据呈现更直观（增加具体数值）
        3. 整治建议更可落地（明确责任部门、时间节点、预算）
        """
        
        try:
            response = await self.chat([{"role": "user", "content": prompt}])
            return response
        except Exception as e:
            logger.error(f"报告优化失败：{str(e)}")
            return f"报告优化失败：{str(e)}"


# 全局 AI 服务实例
ai_service = AIService()
