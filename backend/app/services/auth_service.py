from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import SendCodeRequest, LoginRequest
from app.core.security import generate_verification_code, create_access_token
import json
import os


# 模拟验证码存储（实际项目中应使用Redis）
verification_codes = {}


class AuthService:
    """认证服务"""
    
    @staticmethod
    async def send_verification_code(db: AsyncSession, request: SendCodeRequest) -> bool:
        """发送验证码"""
        phone = request.phone
        
        # 生成验证码
        code = generate_verification_code()
        
        # 存储验证码（实际项目中应使用Redis，并设置过期时间）
        verification_codes[phone] = code
        
        # 模拟短信发送（实际项目中应集成短信服务）
        print(f"向手机号 {phone} 发送验证码: {code}")
        
        # 在开发环境中，直接返回成功
        return True
    
    @staticmethod
    async def login(db: AsyncSession, request: LoginRequest) -> Optional[dict]:
        """用户登录"""
        phone = request.phone
        code = request.code
        
        # 验证验证码
        stored_code = verification_codes.get(phone)
        
        # 在开发环境中，允许使用固定验证码 "123456"
        if code != "123456" and code != stored_code:
            return None
        
        # 查询用户
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        
        # 如果用户不存在，创建新用户
        if not user:
            user = User(
                phone=phone,
                nickname=f"用户{phone[-4:]}"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": str(user.id), "phone": user.phone})
        
        return {
            "token": access_token,
            "user": {
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar": user.avatar
            }
        }
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
