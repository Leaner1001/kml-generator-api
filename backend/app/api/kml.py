from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.kml import KMLGenerateResponse, GenerateHistoryResponse
from app.services.kml_service import KMLService
from app.services.file_service import FileService
from .user import get_current_user_id
import json


router = APIRouter(prefix="/api/kml", tags=["KML生成"])


@router.post("/generate", response_model=KMLGenerateResponse, summary="生成KML文件")
async def generate_kml(
    request: Request,
    file_id: str = Query(..., description="文件ID"),
    layer_type: str = Query(..., description="图层类型"),
    config: str = Query(None, description="图层配置（JSON格式）"),
    db: AsyncSession = Depends(get_db)
):
    """生成KML文件"""
    try:
        # 验证用户身份
        user_id = get_current_user_id(request)
        
        # 解析配置
        config_dict = None
        if config:
            config_dict = json.loads(config)
        
        # 生成KML
        kml_service = KMLService()
        result = await kml_service.generate_kml(db, user_id, file_id, layer_type, config_dict)
        
        return KMLGenerateResponse(
            code=0,
            message="生成成功",
            kml_url=result["kml_url"],
            history_id=result["history_id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/history", response_model=GenerateHistoryResponse, summary="获取生成历史")
async def get_history(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的KML生成历史"""
    try:
        # 验证用户身份
        user_id = get_current_user_id(request)
        
        # 获取历史记录
        kml_service = KMLService()
        history_list = await kml_service.get_generate_history(db, user_id)
        
        return GenerateHistoryResponse(
            code=0,
            message="获取成功",
            data=history_list
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/download", summary="下载KML文件")
async def download_kml(
    request: Request,
    filename: str = Query(..., description="KML文件名")
):
    """下载KML文件"""
    try:
        # 验证用户身份
        get_current_user_id(request)
        
        # 获取文件路径
        file_service = FileService()
        kml_path = file_service.get_kml_path(filename)
        
        if not kml_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件
        return FileResponse(
            path=kml_path,
            filename=filename,
            media_type="application/vnd.google-earth.kml+xml"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
