from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础信息"""
    phone: str
    nickname: str
    avatar: Optional[str] = None


class UserCreate(UserBase):
    """创建用户请求"""
    pass


class UserUpdate(BaseModel):
    """更新用户请求"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class User(UserBase):
    """用户信息响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """用户信息响应"""
    code: int = 0
    message: str = "获取成功"
    user: User
