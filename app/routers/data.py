"""
社区达人路由 - 真实数据导入、核验、入表
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.data_record import DataRecord
from app.models.file import File as FileModel
from app.schemas.data import DataRecordCreate, DataRecordResponse
from app.services.data_engine import data_engine
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
    支持：Excel/CSV/PDF/Word/图片/音频/视频
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
        
        # 创建文件记录
        db_file = FileModel(
            name=unique_name,
            original_name=file.filename,
            file_type=file_type,
            size=len(content),
            url=f"/uploads/{unique_name}"
        )
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        
        return {
            "success": True,
            "file_id": db_file.id,
            "file_name": unique_name,
            "file_type": file_type
        }
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_data(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    真实数据导入
    """
    # 获取文件记录
    result = await db.execute(
        FileModel.__table__.select().where(FileModel.id == file_id)
    )
    file_record = result.first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not os.path.exists(file_record.url.replace("/uploads/", "")):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 调用真实数据引擎
    file_path = file_record.url.replace("/uploads/", "")
    import_result = await data_engine.import_data(file_path, file_record.file_type)
    
    if not import_result["success"]:
        raise HTTPException(status_code=500, detail=import_result.get("error", "导入失败"))
    
    # 创建数据记录
    data_record = DataRecord(
        file_id=file_id,
        data_type="import",
        data=import_result.get("cleaned_data", {}),
        validation_result=import_result.get("validation_result", {}),
        record_count=import_result.get("record_count", 0),
        status="imported"
    )
    db.add(data_record)
    await db.commit()
    await db.refresh(data_record)
    
    return {
        "success": True,
        "data_record_id": data_record.id,
        "import_result": import_result
    }


@router.post("/validate/{record_id}")
async def validate_data(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    真实数据核验
    """
    # 获取数据记录
    result = await db.execute(
        DataRecord.__table__.select().where(DataRecord.id == record_id)
    )
    record = result.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="数据记录不存在")
    
    # 调用真实核验引擎
    validation_result = await data_engine._validate_data(record.data)
    
    # 更新记录
    record.validation_result = validation_result
    record.status = "validated"
    
    await db.commit()
    await db.refresh(record)
    
    return {
        "success": True,
        "record_id": record_id,
        "validation_result": validation_result
    }


@router.post("/enter/{record_id}")
async def enter_data(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    确认入表
    """
    # 获取数据记录
    result = await db.execute(
        DataRecord.__table__.select().where(DataRecord.id == record_id)
    )
    record = result.first()
    
    if not record:
        raise HTTPException(status_code=404, detail="数据记录不存在")
    
    if record.status != "validated":
        raise HTTPException(status_code=400, detail="数据未核验，无法入表")
    
    # 更新记录状态
    record.status = "entered"
    
    await db.commit()
    await db.refresh(record)
    
    return {
        "success": True,
        "record_id": record_id,
        "message": f"已入表成功！共 {record.record_count} 条数据"
    }


@router.get("/query")
async def query_data(
    community: str = None,
    data_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    真实数据查询
    """
    query_result = await data_engine.query_data(community, data_type)
    
    return query_result


@router.post("/compare")
async def compare_data(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db)
):
    """
    真实数据对比
    """
    compare_result = await data_engine.compare_data(start_date, end_date)
    
    return compare_result
