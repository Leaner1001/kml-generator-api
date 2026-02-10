from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.user import UserProfileResponse, UserUpdate
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/user", tags=["用户"])


def get_current_user_id(request: Request) -> int:
    """从请求中获取当前用户ID"""
    # 从请求头获取token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少认证token")
    
    # 解析token
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    try:
        user_id = int(payload.get("sub"))
        return user_id
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="无效的token")


@router.get("/profile", response_model=UserProfileResponse, summary="获取用户信息")
async def get_profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    try:
        user_id = get_current_user_id(request)
        user = await AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserProfileResponse(
            code=0,
            message="获取成功",
            user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.put("/profile", response_model=UserProfileResponse, summary="更新用户信息")
async def update_profile(
    request: Request,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    try:
        user_id = get_current_user_id(request)
        user = await AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新用户信息
        if update_data.nickname:
            user.nickname = update_data.nickname
        if update_data.avatar:
            user.avatar = update_data.avatar
        
        await db.commit()
        await db.refresh(user)
        
        return UserProfileResponse(
            code=0,
            message="更新成功",
            user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
