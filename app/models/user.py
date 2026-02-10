from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GenerateHistory(Base):
    """生成历史模型"""
    __tablename__ = "generate_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    layer_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    kml_url = Column(String, nullable=False)
    status = Column(String, nullable=False, default="success")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
