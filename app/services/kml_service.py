import os
import pandas as pd
import simplekml
import math
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import GenerateHistory
from app.services.file_service import FileService
from fastapi import HTTPException


class KMLService:
    """KML生成服务"""
    
    def __init__(self):
        """初始化KML服务"""
        self.file_service = FileService()
    
    async def generate_kml(self, db: AsyncSession, user_id: int, file_id: str, layer_type: str, config: Optional[Dict[str, Any]] = None) -> dict:
        """生成KML文件"""
        # 获取文件路径
        file_path = self.file_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 读取文件
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件读取失败: {str(e)}")
        
        # 根据图层类型生成KML
        try:
            if layer_type == "sector":
                kml_content = self.generate_sector_layer(df, config)
            elif layer_type == "rsrp":
                kml_content = self.generate_rsrp_layer(df, config)
            elif layer_type == "facility":
                kml_content = self.generate_facility_layer(df, config)
            else:
                raise HTTPException(status_code=400, detail="不支持的图层类型")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"KML生成失败: {str(e)}")
        
        # 保存KML文件
        kml_filename = self.file_service.save_kml_file(kml_content, layer_type)
        kml_url = f"/api/kml/download?filename={kml_filename}"
        
        # 记录生成历史
        history = GenerateHistory(
            user_id=user_id,
            layer_type=layer_type,
            file_name=os.path.basename(file_path),
            kml_url=kml_url,
            status="success"
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
        
        return {
            "kml_url": kml_url,
            "history_id": history.id,
            "kml_filename": kml_filename
        }
    
    def generate_sector_layer(self, df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> bytes:
        """生成基站扇区图层"""
        # 默认配置
        default_config = {
            "lon_col": "经度",
            "lat_col": "纬度",
            "azimuth_col": "方向角",
            "pci_col": "PCI",
            "tac_col": "TAC",
            "cell_name_col": "小区名称",
            "coverage_col": "覆盖类别"
        }
        
        # 合并配置
        if config:
            default_config.update(config)
        config = default_config
        
        # 验证必要字段
        required_cols = [config["lon_col"], config["lat_col"], config["azimuth_col"], 
                        config["pci_col"], config["tac_col"], config["cell_name_col"]]
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要字段: {col}")
        
        # 创建KML对象
        kml = simplekml.Kml(name="基站扇区图层")
        
        # 创建文件夹
        base_station_folder = kml.newfolder(name="基站")
        cell_sector_folder = kml.newfolder(name="小区扇区")
        
        # PCI颜色映射
        pci_colors = {
            0: simplekml.Color.red,
            1: simplekml.Color.yellow,
            2: simplekml.Color.blue
        }
        
        # 处理数据
        for _, row in df.iterrows():
            try:
                # 获取数据
                cell_name = str(row[config["cell_name_col"]])
                base_station_name = cell_name.split('-')[0] if '-' in cell_name else "未知基站"
                pci = int(row[config["pci_col"]])
                color_index = pci % 3
                azimuth = float(row[config["azimuth_col"]])
                tac = str(row[config["tac_col"]])
                center_lon = float(row[config["lon_col"]])
                center_lat = float(row[config["lat_col"]])
                
                # 覆盖类型
                coverage_type = "室外"
                if config["coverage_col"] in df.columns:
                    coverage_type = str(row[config["coverage_col"]])
                
                # 生成扇形
                radius = 0.0005 if "室内" in coverage_type else 0.001
                points = [(center_lon, center_lat)]
                
                # 计算扇形边界点
                for angle in range(int(azimuth) - 60, int(azimuth) + 61, 5):
                    rad_angle = math.radians(angle)
                    delta_lon = radius * math.sin(rad_angle)
                    delta_lat = radius * math.cos(rad_angle)
                    points.append((center_lon + delta_lon, center_lat + delta_lat))
                
                # 创建多边形
                pol = cell_sector_folder.newpolygon(name=cell_name)
                pol.outerboundaryis = points
                pol.style.polystyle.color = simplekml.Color.changealphaint(80, pci_colors[color_index])
                pol.style.polystyle.outline = 1
                pol.style.linestyle.color = pci_colors[color_index]
                pol.style.linestyle.width = 2
                
                # 创建基站点
                point = base_station_folder.newpoint(
                    name=base_station_name,
                    coords=[(center_lon, center_lat)]
                )
                point.style.iconstyle.color = pci_colors[color_index]
                point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/pink-pushpin.png'
                
                # 添加描述
                point.description = f"<div style='font-family:Arial, sans-serif; font-size:13px;'>"
                point.description += f"<b>基站信息</b><br/>"
                point.description += f"• 基站名称: <font color='blue'>{base_station_name}</font><br/>"
                point.description += f"• 小区名称: <font color='blue'>{cell_name}</font><br/>"
                point.description += f"• PCI: <font color='red'>{pci}</font><br/>"
                point.description += f"• TAC: {tac}<br/>"
                point.description += f"• 方向角: {azimuth}°<br/>"
                point.description += f"• 覆盖类别: <b>{coverage_type}</b><br/>"
                point.description += f"<br/><b>位置信息</b><br/>"
                point.description += f"• 经度: {center_lon}<br/>"
                point.description += f"• 纬度: {center_lat}"
                point.description += f"</div>"
                
            except Exception:
                continue
        
        # 保存为字节
        return kml.kml().encode('utf-8')
    
    def generate_rsrp_layer(self, df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> bytes:
        """生成RSRP点图层"""
        # 默认配置
        default_config = {
            "lon_col": "经度",
            "lat_col": "纬度",
            "rsrp_col": "RSRP"
        }
        
        # 合并配置
        if config:
            default_config.update(config)
        config = default_config
        
        # 验证必要字段
        required_cols = [config["lon_col"], config["lat_col"], config["rsrp_col"]]
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要字段: {col}")
        
        # 创建KML对象
        kml = simplekml.Kml(name="RSRP点图层")
        
        # 处理数据
        for _, row in df.iterrows():
            try:
                # 获取数据
                rsrp_value = float(row[config["rsrp_col"]])
                lon = float(row[config["lon_col"]])
                lat = float(row[config["lat_col"]])
                
                # 根据RSRP值确定颜色
                if rsrp_value > -85:
                    color = simplekml.Color.green
                    strength = "极佳"
                elif rsrp_value > -95:
                    color = simplekml.Color.yellow
                    strength = "良好"
                elif rsrp_value > -105:
                    color = simplekml.Color.orange
                    strength = "中等"
                elif rsrp_value > -120:
                    color = simplekml.Color.red
                    strength = "较弱"
                else:
                    color = simplekml.Color.black
                    strength = "极弱"
                
                # 创建点
                point = kml.newpoint(
                    coords=[(lon, lat)]
                )
                point.style.iconstyle.color = color
                point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/dot.png'
                
                # 根据信号强度调整图标大小
                if rsrp_value > -85:
                    point.style.iconstyle.scale = 1.2
                elif rsrp_value > -95:
                    point.style.iconstyle.scale = 1.0
                elif rsrp_value > -105:
                    point.style.iconstyle.scale = 0.9
                elif rsrp_value > -120:
                    point.style.iconstyle.scale = 0.8
                else:
                    point.style.iconstyle.scale = 0.7
                
                # 添加描述
                point.description = f"<div style='font-family:Arial, sans-serif; font-size:13px;'>"
                point.description += f"<b>信号强度信息</b><br/>"
                point.description += f"• RSRP值: <font color='blue'><b>{rsrp_value} dBm</b></font><br/>"
                point.description += f"• 信号评级: <font color='green'><b>{strength}</b></font><br/>"
                point.description += f"<br/><b>位置信息</b><br/>"
                point.description += f"• 经度: {lon}<br/>"
                point.description += f"• 纬度: {lat}"
                point.description += f"</div>"
                
            except Exception:
                continue
        
        # 保存为字节
        return kml.kml().encode('utf-8')
    
    def generate_facility_layer(self, df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> bytes:
        """生成光交/机房图层"""
        # 默认配置
        default_config = {
            "lon_col": "经度",
            "lat_col": "纬度",
            "name_col": "名称",
            "type_col": "类型"
        }
        
        # 合并配置
        if config:
            default_config.update(config)
        config = default_config
        
        # 验证必要字段
        required_cols = [config["lon_col"], config["lat_col"], config["name_col"]]
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要字段: {col}")
        
        # 创建KML对象
        kml = simplekml.Kml(name="光交/机房图层")
        
        # 处理数据
        for _, row in df.iterrows():
            try:
                # 获取数据
                name = str(row[config["name_col"]])
                lon = float(row[config["lon_col"]])
                lat = float(row[config["lat_col"]])
                
                # 设施类型
                facility_type = "光交"
                if config["type_col"] in df.columns:
                    facility_type = str(row[config["type_col"]])
                
                # 创建点
                point = kml.newpoint(
                    name=name,
                    coords=[(lon, lat)]
                )
                
                # 根据类型设置图标
                if "光交" in facility_type:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png'
                elif "机房" in facility_type:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
                else:
                    point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
                
                point.style.iconstyle.scale = 1.1
                
                # 添加描述
                point.description = f"<div style='font-family:Arial, sans-serif; font-size:13px;'>"
                point.description += f"<b>设施信息</b><br/>"
                point.description += f"• 名称: <font color='blue'><b>{name}</b></font><br/>"
                point.description += f"• 类型: <font color='green'><b>{facility_type}</b></font><br/>"
                point.description += f"<br/><b>位置信息</b><br/>"
                point.description += f"• 经度: {lon}<br/>"
                point.description += f"• 纬度: {lat}"
                point.description += f"</div>"
                
            except Exception:
                continue
        
        # 保存为字节
        return kml.kml().encode('utf-8')
    
    async def get_generate_history(self, db: AsyncSession, user_id: int) -> list:
        """获取生成历史"""
        result = await db.execute(
            select(GenerateHistory)
            .where(GenerateHistory.user_id == user_id)
            .order_by(GenerateHistory.created_at.desc())
        )
        history_list = result.scalars().all()
        return history_list
