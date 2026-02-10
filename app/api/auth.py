from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import SendCodeRequest, LoginRequest, LoginResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/send_code", summary="发送验证码")
async def send_code(request: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    """发送短信验证码"""
    try:
        success = await AuthService.send_verification_code(db, request)
        if success:
            return {"code": 0, "message": "验证码发送成功"}
        else:
            raise HTTPException(status_code=500, detail="验证码发送失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录（支持手机号+验证码登录）"""
    try:
        result = await AuthService.login(db, request)
        if result:
            return LoginResponse(
                code=0,
                message="登录成功",
                token=result["token"],
                user=result["user"]
            )
        else:
            raise HTTPException(status_code=401, detail="验证码错误")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
