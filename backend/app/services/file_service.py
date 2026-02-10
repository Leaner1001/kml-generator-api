import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class FileService:
    """文件服务"""
    
    def __init__(self):
        """初始化文件服务"""
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.KML_DIR, exist_ok=True)
    
    async def upload_file(self, file: UploadFile) -> dict:
        """上传文件"""
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="只支持Excel和CSV文件")
        
        # 验证文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()  # 获取文件大小
        file.file.seek(0)  # 重置文件指针
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"文件大小超过限制（最大{settings.MAX_FILE_SIZE // 1024 // 1024}MB）")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_ext}"
        stored_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
        
        # 保存文件
        try:
            with open(stored_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
        
        return {
            "file_id": file_id,
            "file_name": file.filename,
            "stored_path": stored_path
        }
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """获取文件路径"""
        # 查找文件
        for ext in ['.xlsx', '.xls', '.csv']:
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
            if os.path.exists(file_path):
                return file_path
        return None
    
    def save_kml_file(self, kml_content: bytes, layer_type: str) -> str:
        """保存KML文件"""
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        stored_filename = f"{layer_type}_{file_id}.kml"
        stored_path = os.path.join(settings.KML_DIR, stored_filename)
        
        # 保存文件
        try:
            with open(stored_path, "wb") as f:
                f.write(kml_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"KML文件保存失败: {str(e)}")
        
        return stored_filename
    
    def get_kml_path(self, kml_filename: str) -> Optional[str]:
        """获取KML文件路径"""
        kml_path = os.path.join(settings.KML_DIR, kml_filename)
        if os.path.exists(kml_path):
            return kml_path
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
