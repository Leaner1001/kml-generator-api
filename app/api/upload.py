from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.kml import FileUploadResponse
from app.services.file_service import FileService
from .user import get_current_user_id


router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/file", response_model=FileUploadResponse, summary="上传文件")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传Excel或CSV文件"""
    try:
        # 验证用户身份
        get_current_user_id(request)
        
        # 上传文件
        file_service = FileService()
        result = await file_service.upload_file(file)
        
        return FileUploadResponse(
            code=0,
            message="上传成功",
            file_id=result["file_id"],
            file_name=result["file_name"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
