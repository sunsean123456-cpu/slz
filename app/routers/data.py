"""
社区达人路由（数据管理）
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.data_record import DataRecord
from app.models.file import File as FileModel
from app.schemas.data import DataRecordCreate, DataRecordResponse
from app.services.file_processor import FileProcessor
from app.schemas.multimodal import MultimodalInput
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=DataRecordResponse)
async def create_data_record(
    data: DataRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建数据记录
    支持：上传文件、输入文本、多模态输入
    """
    try:
        # 创建数据记录
        record = DataRecord(
            project_id=data.project_id,
            file_id=data.file_id,
            community=data.community,
            data_type=data.data_type,
            data=data.data,
            record_count=len(data.data) if isinstance(data.data, list) else 1,
            status="pending"
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        
        return record
    except Exception as e:
        logger.error(f"创建数据记录失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/{record_id}")
async def validate_data(record_id: int, db: AsyncSession = Depends(get_db)):
    """
    数据校验
    检查格式错误、空值、格式不统一等
    """
    # 获取数据记录
    result = await db.execute(
        DataRecord.__table__.select().where(DataRecord.id == record_id)
    )
    record = result.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="数据记录不存在")
    
    # 数据校验逻辑
    validation_result = await validate_data_logic(record.data)
    
    # 更新记录
    record.validation_result = validation_result
    record.valid_count = validation_result.get("valid_count", 0)
    record.invalid_count = validation_result.get("invalid_count", 0)
    record.status = "validated"
    
    await db.commit()
    await db.refresh(record)
    
    return {
        "record_id": record_id,
        "validation_result": validation_result
    }


@router.post("/enter/{record_id}")
async def enter_data(record_id: int, db: AsyncSession = Depends(get_db)):
    """
    确认入表
    将校验通过的数据写入数据库
    """
    # 获取数据记录
    result = await db.execute(
        DataRecord.__table__.select().where(DataRecord.id == record_id)
    )
    record = result.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="数据记录不存在")
    
    if record.status != "validated":
        raise HTTPException(status_code=400, detail="数据未校验，无法入表")
    
    # 更新记录状态
    record.status = "entered"
    record.entered_at = None  # 实际应设置为当前时间
    
    await db.commit()
    await db.refresh(record)
    
    return {
        "success": True,
        "record_id": record_id,
        "message": f"已入表成功！共 {record.valid_count} 条数据"
    }


@router.get("/", response_model=list[DataRecordResponse])
async def list_data_records(
    project_id: int = None,
    community: str = None,
    data_type: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    查询数据记录列表
    """
    query = select(DataRecord)
    
    if project_id:
        query = query.where(DataRecord.project_id == project_id)
    if community:
        query = query.where(DataRecord.community == community)
    if data_type:
        query = query.where(DataRecord.data_type == data_type)
    if status:
        query = query.where(DataRecord.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return records


@router.delete("/{record_id}")
async def delete_data_record(record_id: int, db: AsyncSession = Depends(get_db)):
    """删除数据记录"""
    result = await db.execute(
        DataRecord.__table__.select().where(DataRecord.id == record_id)
    )
    record = result.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="数据记录不存在")
    
    await db.delete(record)
    await db.commit()
    
    return {"success": True, "message": "数据记录已删除"}


async def process_multimodal(input_data: MultimodalInput) -> dict:
    """
    处理多模态输入（社区达人模块）
    
    Args:
        input_data: 多模态输入数据
    
    Returns:
        处理结果
    """
    result = {
        "module": "data",
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


async def validate_data_logic(data: dict) -> dict:
    """
    数据校验逻辑
    
    Args:
        data: 数据内容
    
    Returns:
        校验结果
    """
    valid_count = 0
    invalid_count = 0
    errors = []
    
    # 简单校验逻辑（实际应更复杂）
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # 检查必填字段
                if "name" not in item or not item["name"]:
                    errors.append({"row": i, "field": "name", "error": "姓名不能为空"})
                    invalid_count += 1
                else:
                    valid_count += 1
            else:
                errors.append({"row": i, "error": "数据格式错误"})
                invalid_count += 1
    else:
        errors.append({"error": "数据格式错误，应为列表"})
        invalid_count = 1
    
    return {
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "errors": errors,
        "status": "completed" if not errors else "has_errors"
    }
