from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式错误")
        return v


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式错误")
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """验证验证码格式"""
        if not v.isdigit() or len(v) != 6:
            raise ValueError("验证码格式错误")
        return v


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    phone: str
    nickname: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 0
    message: str = "登录成功"
    token: str
    user: UserInfo
