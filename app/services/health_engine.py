"""
城市体检引擎 - 真实报告审查、图表生成
"""
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.health_report import HealthReport
from app.services.document_parser import document_parser

logger = logging.getLogger(__name__)


class HealthEngine:
    """城市体检引擎"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    async def review_report(self, report_content: str) -> Dict[str, Any]:
        """
        真实报告审查
        
        Args:
            report_content: 报告内容
        
        Returns:
            审查结果
        """
        try:
            # 1. 使用 AI 进行报告审查
            review_result = await self._analyze_report(report_content)
            
            # 2. 生成问题清单
            issues = await self._generate_issues(review_result)
            
            # 3. 生成修改建议
            suggestions = await self._generate_suggestions(issues)
            
            return {
                "success": True,
                "score": review_result.get("score", 0),
                "level": review_result.get("level", "B"),
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"报告审查失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_report(self, content: str) -> Dict[str, Any]:
        """AI 报告分析"""
        prompt = f"""
        请对以下城市体检报告进行审查：
        
        {content}
        
        请从以下维度进行评分（满分 100 分）：
        1. 数据准确性（30 分）
        2. 逻辑一致性（25 分）
        3. 格式规范性（20 分）
        4. 结论完整性（15 分）
        5. 建议可落地性（10 分）
        
        请返回以下格式的 JSON：
        {{
            "score": 92,
            "level": "A",
            "dimensions": {{
                "data_accuracy": 28,
                "logic_consistency": 23,
                "format_standard": 18,
                "conclusion_completeness": 14,
                "suggestion_practicality": 9
            }},
            "issues": [
                {{
                    "title": "问题标题",
                    "description": "问题描述",
                    "severity": "高/中/低",
                    "suggestion": "修改建议"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的城市体检报告审查专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"报告分析失败：{str(e)}")
            return {"score": 0, "level": "B", "issues": []}
    
    async def _generate_issues(self, review_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成问题清单"""
        return review_result.get("issues", [])
    
    async def _generate_suggestions(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成修改建议"""
        suggestions = []
        
        for issue in issues:
            suggestions.append({
                "issue": issue.get("title", ""),
                "suggestion": issue.get("suggestion", ""),
                "priority": "high" if issue.get("severity") == "高" else "medium" if issue.get("severity") == "中" else "low"
            })
        
        return suggestions
    
    async def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成体检报告
        
        Args:
            data: 体检数据
        
        Returns:
            报告内容
        """
        try:
            prompt = f"""
            请根据以下数据生成城市体检报告：
            
            {json.dumps(data, ensure_ascii=False, indent=2)}
            
            报告应包含：
            1. 总体概况与综合评估
            2. 各维度详细分析
            3. 问题诊断与原因分析
            4. 整治建议与实施路径
            5. 年度对比与趋势预测
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的城市体检报告撰写专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return {
                "success": True,
                "report": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"生成报告失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def optimize_report(self, content: str) -> Dict[str, Any]:
        """
        优化报告
        
        Args:
            content: 原始报告内容
        
        Returns:
            优化后的报告
        """
        try:
            prompt = f"""
            请优化以下城市体检报告：
            
            {content}
            
            优化要求：
            1. 文字表述更精准（避免模糊描述）
            2. 数据呈现更直观（增加具体数值）
            3. 整治建议更可落地（明确责任部门、时间节点、预算）
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的城市体检报告优化专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return {
                "success": True,
                "optimized_report": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"优化报告失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成可视化图表
        
        Args:
            data: 图表数据
        
        Returns:
            图表配置
        """
        try:
            prompt = f"""
            请根据以下数据生成可视化图表配置：
            
            {json.dumps(data, ensure_ascii=False, indent=2)}
            
            请返回 ECharts 配置，包含：
            1. 柱状图
            2. 对比图
            3. 雷达图
            4. 折线图
            5. 饼图
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的数据可视化专家，擅长 ECharts 配置。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"生成图表失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_ppt(self, report_content: str) -> Dict[str, Any]:
        """
        生成汇报 PPT
        
        Args:
            report_content: 报告内容
        
        Returns:
            PPT 内容
        """
        try:
            prompt = f"""
            请根据以下报告内容生成 12 页汇报 PPT：
            
            {report_content}
            
            PPT 结构：
            第 1 页：封面 + 体检概况
            第 2 页：综合得分雷达图
            第 3-7 页：各维度详细分析
            第 8 页：问题清单 + 根因分析
            第 9 页：整治方案（优先级矩阵）
            第 10 页：年度对比趋势
            第 11 页：资金需求 + 部门分工
            第 12 页：下一步工作计划
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的 PPT 制作专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return {
                "success": True,
                "ppt_content": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"生成 PPT 失败：{str(e)}")
            return {"success": False, "error": str(e)}


# 全局体检引擎实例
health_engine = HealthEngine()
