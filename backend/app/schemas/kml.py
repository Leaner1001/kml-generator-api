from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class KMLGenerateRequest(BaseModel):
    """KML生成请求"""
    file_id: str = Field(..., description="文件ID")
    layer_type: str = Field(..., description="图层类型")
    config: Optional[Dict[str, Any]] = Field(default=None, description="图层配置")


class KMLGenerateResponse(BaseModel):
    """KML生成响应"""
    code: int = 0
    message: str = "生成成功"
    kml_url: str
    history_id: int


class GenerateHistoryItem(BaseModel):
    """生成历史项"""
    id: int
    layer_type: str
    file_name: str
    kml_url: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GenerateHistoryResponse(BaseModel):
    """生成历史响应"""
    code: int = 0
    message: str = "获取成功"
    data: List[GenerateHistoryItem]


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    code: int = 0
    message: str = "上传成功"
    file_id: str
    file_name: str
