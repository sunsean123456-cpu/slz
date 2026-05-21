"""
文件管理路由
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.file import File as FileModel
from app.schemas.file import FileResponse
from app.services.file_processor import FileProcessor, detect_file_type
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    文件上传接口
    支持：图片、PPT、PDF、Excel、音频、视频等
    """
    try:
        # 生成唯一文件名
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_name = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 检测文件类型
        file_type = detect_file_type(file.filename)
        
        # 创建数据库记录
        db_file = FileModel(
            project_id=project_id,
            name=unique_name,
            original_name=file.filename,
            file_type=file_type,
            size=len(content),
            url=f"/uploads/{unique_name}",
            metadata={
                "content_type": file.content_type,
                "original_name": file.filename
            }
        )
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        
        return db_file
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """获取文件信息"""
    result = await db.execute(
        FileModel.__table__.select().where(FileModel.id == file_id)
    )
    file = result.first()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return file


@router.post("/{file_id}/parse")
async def parse_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """
    解析文件
    支持多模态：图片、PPT、PDF、Excel、音频、视频
    """
    # 获取文件记录
    result = await db.execute(
        FileModel.__table__.select().where(FileModel.id == file_id)
    )
    file = result.first()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 解析文件
    file_path = os.path.join(UPLOAD_DIR, file.name)
    result = await FileProcessor.process_file(file_path, file.file_type)
    
    return {
        "file_id": file_id,
        "file_type": file.file_type,
        "parse_result": result
    }


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """删除文件"""
    # 获取文件记录
    result = await db.execute(
        FileModel.__table__.select().where(FileModel.id == file_id)
    )
    file = result.first()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    file_path = os.path.join(UPLOAD_DIR, file.name)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    await db.delete(file)
    await db.commit()
    
    return {"success": True, "message": "文件已删除"}
