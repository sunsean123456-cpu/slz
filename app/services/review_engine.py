"""
方案评审引擎 - 真实 AI 评审服务
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class ReviewEngine:
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
        # 构建评审提示词
        prompt = f"""
        你是一位专业的城市更新方案评审专家。请对以下{plan_type}方案进行详细评审。
        
        ## 评审要求
        
        请从以下 5 个维度进行评分（满分 100 分）：
        1. **政策合规性**（权重 25%）：是否符合国家及地方政策法规
        2. **技术可行性**（权重 25%）：技术方案是否合理可行
        3. **经济合理性**（权重 20%）：预算编制是否合理，资金筹措是否可行
        4. **社会可接受度**（权重 15%）：居民接受程度，社会风险
        5. **实施可操作性**（权重 15%）：进度安排是否合理，责任是否明确
        
        ## 评审内容
        
        {plan_content}
        
        ## 输出格式
        
        请严格按照以下 JSON 格式输出，不要包含其他内容：
        
        ```json
        {{
            "total_score": 85.5,
            "level": "良好",
            "dimensions": {{
                "policy_compliance": {{
                    "score": 88,
                    "weight": 25,
                    "weighted_score": 22.0,
                    "comment": "政策合规性较好，符合《XX市城市更新条例》相关规定"
                }},
                "technical_feasibility": {{
                    "score": 85,
                    "weight": 25,
                    "weighted_score": 21.3,
                    "comment": "技术方案基本可行，但部分工艺需优化"
                }},
                "economic_rationality": {{
                    "score": 78,
                    "weight": 20,
                    "weighted_score": 15.6,
                    "comment": "预算编制偏低，拆迁补偿费用低于市场均价"
                }},
                "social_acceptance": {{
                    "score": 80,
                    "weight": 15,
                    "weighted_score": 12.0,
                    "comment": "居民沟通机制不够完善"
                }},
                "implementation_operability": {{
                    "score": 82,
                    "weight": 15,
                    "weighted_score": 12.3,
                    "comment": "进度计划未考虑雨季因素"
                }}
            }},
            "issues": [
                {{
                    "id": 1,
                    "title": "拆迁补偿预算偏低",
                    "description": "预算编制中拆迁补偿费用低于市场均价 12%，可能导致居民拒签",
                    "severity": "high",
                    "category": "经济合理性",
                    "suggestion": "建议上调拆迁补偿标准至市场均价，增加过渡期安置补贴 85 万元"
                }},
                {{
                    "id": 2,
                    "title": "缺少过渡期安置补贴",
                    "description": "居民安置方案未明确过渡期补贴标准",
                    "severity": "medium",
                    "category": "社会可接受度",
                    "suggestion": "建议补充过渡期补贴标准：2000 元/月/户"
                }},
                {{
                    "id": 3,
                    "title": "进度计划未考虑雨季",
                    "description": "施工计划未预留雨季缓冲期，可能导致工期延误 15-20 天",
                    "severity": "medium",
                    "category": "实施可操作性",
                    "suggestion": "建议增加雨季缓冲期 15 天，调整关键路径"
                }}
            ],
            "optimization_plan": {{
                "budget_adjustment": "拆迁补偿费用上调 12%，增加过渡期补贴 85 万",
                "schedule_optimization": "增加雨季缓冲期 15 天，采用装配式施工缩短工期 20%",
                "communication_mechanism": "建立'一户一策'沟通机制，设立居民咨询服务中心",
                "technical_improvement": "建议采用装配式施工工艺，提高施工效率"
            }},
            "risks": [
                {{
                    "level": "high",
                    "type": "资金风险",
                    "description": "拆迁补偿预算偏低 342 万，可能导致居民拒签",
                    "suggestion": "上调拆迁补偿标准至市场均价"
                }},
                {{
                    "level": "medium",
                    "type": "进度风险",
                    "description": "未考虑雨季因素，可能导致工期延误",
                    "suggestion": "增加雨季缓冲期"
                }},
                {{
                    "level": "low",
                    "type": "技术风险",
                    "description": "传统施工工艺工期较长",
                    "suggestion": "考虑装配式施工"
                }}
            ]
        }}
        ```
        """
        
        try:
            # 调用 AI 进行评审
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的城市更新方案评审专家，擅长从政策合规性、技术可行性、经济合理性、社会可接受度、实施可操作性五个维度对方案进行全面评审。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # 解析 AI 回复
            ai_response = response.choices[0].message.content
            
            # 提取 JSON
            json_str = self._extract_json(ai_response)
            result = json.loads(json_str)
            
            return {
                "success": True,
                "review_result": result,
                "ai_raw_response": ai_response
            }
            
        except Exception as e:
            logger.error(f"方案评审失败：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_json(self, text: str) -> str:
        """从 AI 回复中提取 JSON"""
        import re
        
        # 尝试提取 ```json ... ``` 中的内容
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # 尝试提取 { ... } 中的内容
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text


# 全局评审引擎实例
review_engine = ReviewEngine()
