"""
石榴籽城市更新 Agent - 后端服务
FastAPI + PostgreSQL + AI 服务
"""
import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import logging
from contextlib import asynccontextmanager

# 导入配置
from app.config import settings
from app.database import engine, Base
from app.routers import data, policy, health, plan, pricing, auth, files, ai

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 石榴籽城市更新 Agent 启动中...")
    
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ 数据库表创建完成")
    logger.info("🎉 石榴籽城市更新 Agent 启动成功！")
    
    yield
    
    # 关闭时清理
    logger.info("👋 石榴籽城市更新 Agent 关闭中...")
    await engine.dispose()
    logger.info("✅ 数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="石榴籽城市更新 Agent",
    description="AI 驱动的城市更新工作平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 挂载静态文件目录（用于存储上传的文件）
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(files.router, prefix="/api/files", tags=["文件管理"])
app.include_router(data.router, prefix="/api/data", tags=["社区达人"])
app.include_router(policy.router, prefix="/api/policy", tags=["政策咨询"])
app.include_router(health.router, prefix="/api/health", tags=["城市体检"])
app.include_router(plan.router, prefix="/api/plan", tags=["方案评审"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["收费/会员"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI 服务"])


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "石榴籽城市更新 Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用石榴籽城市更新 Agent",
        "docs": "/docs",
        "health": "/health"
    }


# 多模态输入接口（核心）
class MultimodalInput(BaseModel):
    """多模态输入模型"""
    text: Optional[str] = None  # 文字输入
    image_url: Optional[str] = None  # 图片 URL
    file_url: Optional[str] = None  # 文件 URL（PPT/PDF/Excel 等）
    audio_url: Optional[str] = None  # 音频 URL
    video_url: Optional[str] = None  # 视频 URL
    module: str = Field(..., description="目标模块：data/policy/health/plan")
    query: str = Field(..., description="用户查询/指令")


@app.post("/api/multimodal")
async def multimodal_input(input_data: MultimodalInput):
    """
    多模态输入接口
    支持：文字、图片、文件、音频、视频
    """
    try:
        # 根据模块路由到对应服务
        if input_data.module == "data":
            result = await data.process_multimodal(input_data)
        elif input_data.module == "policy":
            result = await policy.process_multimodal(input_data)
        elif input_data.module == "health":
            result = await health.process_multimodal(input_data)
        elif input_data.module == "plan":
            result = await plan.process_multimodal(input_data)
        else:
            raise HTTPException(status_code=400, detail=f"未知模块：{input_data.module}")
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"多模态输入处理失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 文件上传接口（支持多模态）
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    文件上传接口
    支持：图片、PPT、PDF、Excel、音频、视频等
    """
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        new_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 返回文件信息
        return {
            "success": True,
            "filename": new_filename,
            "url": f"/uploads/{new_filename}",
            "size": len(content),
            "type": file.content_type,
            "ext": file_ext
        }
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
