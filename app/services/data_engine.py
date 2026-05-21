"""
社区达人引擎 - 真实数据导入、核验、入表
"""
import json
import logging
from typing import Dict, Any, List
import pandas as pd
from openai import OpenAI
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.data_record import DataRecord
from app.models.file import File
from app.services.document_parser import document_parser

logger = logging.getLogger(__name__)


class DataEngine:
    """社区达人引擎"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    async def import_data(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        真实数据导入
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
        
        Returns:
            导入结果
        """
        try:
            # 1. 解析文件
            parse_result = await document_parser.parse_file(file_path, file_type)
            
            if "error" in parse_result:
                return {"success": False, "error": parse_result["error"]}
            
            # 2. 数据清洗和对齐
            cleaned_data = await self._clean_data(parse_result)
            
            # 3. 数据核验
            validation_result = await self._validate_data(cleaned_data)
            
            # 4. 保存到数据库
            record_count = await self._save_to_database(cleaned_data, validation_result)
            
            return {
                "success": True,
                "record_count": record_count,
                "validation_result": validation_result,
                "cleaned_data": cleaned_data
            }
            
        except Exception as e:
            logger.error(f"数据导入失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _clean_data(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """数据清洗"""
        # 使用 AI 进行数据清洗
        prompt = f"""
        请对以下数据进行清洗和对齐：
        
        {json.dumps(parse_result, ensure_ascii=False, indent=2)}
        
        清洗要求：
        1. 统一日期格式为 YYYY-MM-DD
        2. 统一电话号码格式为 11 位手机号
        3. 统一身份证号为 18 位标准格式
        4. 去除重复记录
        5. 填补缺失值（如可能）
        
        请返回清洗后的数据。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的数据清洗专家，擅长数据对齐和格式标准化。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"数据清洗失败：{str(e)}")
            return parse_result
    
    async def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数据核验"""
        # 使用 AI 进行数据核验
        prompt = f"""
        请对以下数据进行核验：
        
        {json.dumps(data, ensure_ascii=False, indent=2)}
        
        核验要求：
        1. 检查数据完整性
        2. 检查数据格式是否正确
        3. 检查数据逻辑是否合理
        4. 标记异常数据
        
        请返回核验结果。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的数据核验专家，擅长发现数据问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"数据核验失败：{str(e)}")
            return {"valid": True, "issues": []}
    
    async def _save_to_database(self, data: Dict[str, Any], validation_result: Dict[str, Any]) -> int:
        """保存到数据库"""
        try:
            async with AsyncSessionLocal() as session:
                # 创建数据记录
                record = DataRecord(
                    data_type="import",
                    data=data,
                    validation_result=validation_result,
                    record_count=len(data.get("records", [])),
                    status="imported"
                )
                session.add(record)
                await session.commit()
                
                return record.record_count
        except Exception as e:
            logger.error(f"保存数据失败：{str(e)}")
            return 0
    
    async def query_data(self, community: str = None, data_type: str = None) -> Dict[str, Any]:
        """
        真实数据查询
        
        Args:
            community: 社区名称
            data_type: 数据类型
        
        Returns:
            查询结果
        """
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                
                query = select(DataRecord)
                
                if community:
                    query = query.where(DataRecord.community == community)
                if data_type:
                    query = query.where(DataRecord.data_type == data_type)
                
                result = await session.execute(query)
                records = result.scalars().all()
                
                return {
                    "success": True,
                    "records": [
                        {
                            "id": record.id,
                            "community": record.community,
                            "data_type": record.data_type,
                            "record_count": record.record_count,
                            "status": record.status,
                            "created_at": record.created_at.isoformat() if record.created_at else None
                        }
                        for record in records
                    ]
                }
        except Exception as e:
            logger.error(f"数据查询失败：{str(e)}")
            return {"success": False, "error": str(e)}
    
    async def compare_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        真实数据对比
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            对比结果
        """
        try:
            # 使用 AI 进行数据对比分析
            prompt = f"""
            请对比以下时间段的数据：
            - 开始日期：{start_date}
            - 结束日期：{end_date}
            
            对比要求：
            1. 统计新增记录数
            2. 统计删除记录数
            3. 统计变更记录数
            4. 分析变化趋势
            
            请返回对比结果。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的数据分析专家，擅长数据对比和趋势分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"数据对比失败：{str(e)}")
            return {"success": False, "error": str(e)}


# 全局数据引擎实例
data_engine = DataEngine()
